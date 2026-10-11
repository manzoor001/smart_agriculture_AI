
import json
from rag_service import RAGService

service = None

try:
    print("Initializing RAG service...")
    service = RAGService()
    print("RAG service initialized successfully.")

    question = (
        "What are the benefits of including summer greengram in rice-wheat cropping systems?"
    )

    print(f"\nQuestion: {question}")
    print("\nRetrieving information and generating an answer...")

    result = service.answer(question)

    print("\n--- RAG RESPONSE ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

except Exception as error:
    print(f"\nTest failed: {type(error).__name__}: {error}")

finally:
    if service is not None:
        service.close()
        print("\nQdrant connection closed.")
