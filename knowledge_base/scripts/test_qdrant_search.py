
from pathlib import Path

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
QDRANT_PATH = BASE_DIR / "qdrant_storage"

COLLECTION_NAME = "agricultural_knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    client = QdrantClient(path=str(QDRANT_PATH))

    try:
        question = input(
            "\nEnter an agricultural question: "
        ).strip()

        if not question:
            print("Please enter a question.")
            return

        question_vector = model.encode(
            question,
            normalize_embeddings=True
        ).tolist()

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=question_vector,
            limit=5,
            with_payload=True
        ).points

        if not results:
            print("No matching passages found.")
            return

        print("\nTop matching passages from Qdrant:\n")

        for index, result in enumerate(results, start=1):
            payload = result.payload or {}

            print(f"Result {index}")
            print(f"Similarity score: {result.score:.4f}")
            print(f"Document: {payload.get('source', 'Unknown')}")
            print(f"Page: {payload.get('page', 'Unknown')}")
            print(f"Passage: {payload.get('text', '')[:500]}")
            print("-" * 60)

    finally:
        client.close()


if __name__ == "__main__":
    main()
