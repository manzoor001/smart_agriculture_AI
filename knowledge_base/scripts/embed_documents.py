from pathlib import Path
import json

from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "processed" / "rag_chunks.jsonl"
OUTPUT_FILE = BASE_DIR / "processed" / "rag_embeddings.jsonl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 16


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Chunks file not found: {INPUT_FILE}")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    chunks = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    if not chunks:
        print("No chunks found.")
        return

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for chunk, vector in zip(chunks, vectors):
            record = {
                **chunk,
                "embedding": vector.tolist(),
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nChunks embedded: {len(chunks)}")
    print(f"Vector dimensions: {len(vectors[0])}")
    print(f"Saved embeddings to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
