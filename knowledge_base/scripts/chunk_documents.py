
from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "processed"
OUTPUT_FILE = INPUT_DIR / "rag_chunks.jsonl"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def clean_text(text):
    """Clean extracted PDF text without removing useful line breaks."""
    text = text.replace("\x0c", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_heading(line):
    """Identify likely section headings in extracted documents."""
    line = line.strip()

    if not line or len(line) > 120:
        return False

    if re.match(r"^(chapter|section|figure|table)\s+\w+", line, re.I):
        return True

    # Short lines ending without normal sentence punctuation
    if (
        len(line.split()) <= 12
        and not re.search(r"[.!?,;:]$", line)
        and not line.endswith((",", ";"))
    ):
        return bool(re.search(r"[A-Za-z]", line))

    return False


def make_sections(text):
    """Separate text at blank lines and likely headings."""
    lines = text.splitlines()
    sections = []
    current_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            if current_lines:
                sections.append(" ".join(current_lines))
                current_lines = []
            continue

        if is_heading(line) and current_lines:
            sections.append(" ".join(current_lines))
            current_lines = []

        current_lines.append(line)

    if current_lines:
        sections.append(" ".join(current_lines))

    return [section.strip() for section in sections if section.strip()]


def split_long_section(section):
    """Split long sections at sentence boundaries where possible."""
    sentences = re.split(r"(?<=[.!?])\s+", section.strip())
    pieces = []
    current = ""

    for sentence in sentences:
        if len(sentence) > CHUNK_SIZE:
            if current:
                pieces.append(current)
                current = ""

            words = sentence.split()
            part = ""

            for word in words:
                candidate = f"{part} {word}".strip()

                if len(candidate) <= CHUNK_SIZE:
                    part = candidate
                else:
                    if part:
                        pieces.append(part)
                    part = word

            if part:
                current = part

        else:
            candidate = f"{current} {sentence}".strip()

            if len(candidate) <= CHUNK_SIZE:
                current = candidate
            else:
                if current:
                    pieces.append(current)
                current = sentence

    if current:
        pieces.append(current)

    return pieces


def split_into_chunks(text):
    text = clean_text(text)
    sections = make_sections(text)

    chunks = []
    current = ""

    for section in sections:
        pieces = split_long_section(section)

        for piece in pieces:
            candidate = f"{current}\n\n{piece}".strip() if current else piece

            if len(candidate) <= CHUNK_SIZE:
                current = candidate
            else:
                if current:
                    chunks.append(current)

                # Only overlap within the same section, not across topics.
                current = piece

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk.strip()]


def process_document(path):
    text = path.read_text(encoding="utf-8")
    pages = re.split(r"--- Page (\d+) ---", text)

    results = []

    # Preserve the page number attached to every chunk.
    for index in range(1, len(pages), 2):
        page_number = int(pages[index])
        page_text = pages[index + 1]

        for chunk in split_into_chunks(page_text):
            results.append({
                "source": path.name,
                "page": page_number,
                "text": chunk,
            })

    return results


def main():
    files = sorted(INPUT_DIR.glob("*.txt"))

    # Ignore generated JSONL files; only process extracted source text.
    files = [path for path in files if path.name != "rag_chunks.jsonl"]

    if not files:
        print(f"No extracted text files found in {INPUT_DIR}")
        return

    all_chunks = []

    for path in files:
        print(f"Chunking: {path.name}")
        chunks = process_document(path)
        all_chunks.extend(chunks)
        print(f"Chunks created: {len(chunks)}")

    with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
        for chunk in all_chunks:
            output_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
