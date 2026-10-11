
from pathlib import Path
import json

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDINGS_FILE = BASE_DIR / "processed" / "rag_embeddings.jsonl"
QDRANT_PATH = BASE_DIR / "qdrant_storage"

# Qdrant configuration
COLLECTION_NAME = "agricultural_knowledge"
VECTOR_SIZE = 384
BATCH_SIZE = 64


def load_embeddings():
    """Load existing chunks and embeddings from JSONL."""
    records = []

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {error}"
                ) from error

            if "embedding" not in record or "text" not in record:
                raise ValueError(
                    f"Missing embedding or text on line {line_number}"
                )

            if len(record["embedding"]) != VECTOR_SIZE:
                raise ValueError(
                    f"Expected {VECTOR_SIZE} embedding values "
                    f"on line {line_number}, but found "
                    f"{len(record['embedding'])}"
                )

            records.append(record)

    return records


def main():
    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Embeddings file not found: {EMBEDDINGS_FILE}"
        )

    print("Loading existing agricultural embeddings...")

    records = load_embeddings()

    if not records:
        print("No embeddings found. Nothing to index.")
        return

    print(f"Loaded {len(records)} chunks.")
    print(f"Qdrant storage directory: {QDRANT_PATH}")

    # Open a persistent, local Qdrant database.
    QDRANT_PATH.mkdir(parents=True, exist_ok=True)

    client = QdrantClient(path=str(QDRANT_PATH))

    try:
        # Rebuild only our dedicated collection when rerunning
        # this indexing script, preventing duplicate or stale data.
        if client.collection_exists(COLLECTION_NAME):
            print("Existing collection found. Rebuilding it...")
            client.delete_collection(COLLECTION_NAME)

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

        print("Qdrant collection created.")

        # Insert chunks in batches.
        for start in range(0, len(records), BATCH_SIZE):
            batch_records = records[start:start + BATCH_SIZE]
            points = []

            for index, record in enumerate(
                batch_records,
                start=start
            ):
                points.append(
                    PointStruct(
                        id=index,
                        vector=record["embedding"],
                        payload={
                            "text": record["text"],
                            "source": record.get("source", "Unknown"),
                            "page": record.get("page", "Unknown")
                        }
                    )
                )

            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points,
                wait=True
            )

            print(
                f"Indexed {min(start + BATCH_SIZE, len(records))}"
                f"/{len(records)} chunks..."
            )

        # Verify the stored point count.
        collection_info = client.get_collection(COLLECTION_NAME)

        print("\nIndexing completed successfully!")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Stored vectors: {collection_info.points_count}")
        print(f"Vector dimensions: {VECTOR_SIZE}")
        print(f"Database location: {QDRANT_PATH}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
