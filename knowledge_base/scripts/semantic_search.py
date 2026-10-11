
from pathlib import Path
import json
import re
import torch

from sentence_transformers import SentenceTransformer, util

BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_FILE = BASE_DIR / "processed" / "rag_embeddings.jsonl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

# Words that commonly appear in agricultural questions and documents.
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "for", "and", "or", "with", "by",
    "how", "what", "which", "can", "do", "does", "farmers",
    "farmer", "improve", "improving", "use", "using"
}


def load_embeddings():
    records = []

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def tokenize(text):
    """Extract lowercase words for keyword matching."""
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def keyword_score(question, document):
    """
    Measure how many important question words occur in a document.
    This is a simple baseline, not a full information-retrieval algorithm.
    """
    question_words = {
        word for word in tokenize(question)
        if word not in STOP_WORDS and len(word) > 1
    }

    if not question_words:
        return 0.0

    document_words = set(tokenize(document))
    matched_words = question_words & document_words

    return len(matched_words) / len(question_words)


def search_knowledge_base(question: str, records: list, model):
    question_embedding = model.encode(
        question,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    document_embeddings = torch.tensor(
        [record["embedding"] for record in records],
        dtype=torch.float32,
    )

    semantic_scores = util.cos_sim(
        question_embedding,
        document_embeddings,
    )[0].tolist()

    results = []

    for index, record in enumerate(records):
        text = record.get("text", "")
        semantic_score = float(semantic_scores[index])
        keyword_match = keyword_score(question, text)

        # Combine semantic meaning and exact keyword overlap.
        hybrid_score = (
            0.70 * semantic_score
            + 0.30 * keyword_match
        )

        results.append({
            "score": round(hybrid_score, 4),
            "semantic_score": round(semantic_score, 4),
            "keyword_score": round(keyword_match, 4),
            "text": text,
            "source": record.get("source", "Unknown"),
            "page": record.get("page", "Unknown"),
        })

    results.sort(key=lambda item: item["score"], reverse=True)

    return results[:min(TOP_K, len(results))]


def main():
    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Embeddings file not found: {EMBEDDINGS_FILE}"
        )

    print("Loading agricultural knowledge base...")
    records = load_embeddings()

    if not records:
        print("No records found.")
        return

    print(f"Loaded {len(records)} chunks.")

    model = SentenceTransformer(MODEL_NAME)

    question = input("\nEnter your agricultural question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    results = search_knowledge_base(question, records, model)

    print("\nMost relevant results (hybrid search):\n")

    for rank, result in enumerate(results, start=1):
        print(
            f"Result {rank} | Hybrid: {result['score']} | "
            f"Semantic: {result['semantic_score']} | "
            f"Keyword: {result['keyword_score']}"
        )
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(result["text"])
        print("-" * 60)


if __name__ == "__main__":
    main()
