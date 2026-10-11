
from pathlib import Path
import re
import requests

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# Project configuration
BASE_DIR = Path(__file__).resolve().parent.parent
QDRANT_PATH = BASE_DIR / "qdrant_storage"

COLLECTION_NAME = "agricultural_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"

TOP_K = 5
CANDIDATE_LIMIT = 20
MIN_RELEVANCE_SCORE = 0.20

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "for", "and", "or", "with", "by",
    "how", "what", "which", "can", "do", "does", "farmers",
    "farmer", "improve", "improving", "use", "using"
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z0-9]+\b", text.lower())


def keyword_score(question: str, document: str) -> float:
    question_words = {
        word for word in tokenize(question)
        if word not in STOP_WORDS and len(word) > 1
    }

    if not question_words:
        return 0.0

    document_words = set(tokenize(document))
    matched_words = question_words & document_words

    return len(matched_words) / len(question_words)


class RAGService:
    """Retrieve agricultural passages and generate grounded answers."""

    def __init__(self):
        if not QDRANT_PATH.exists():
            raise FileNotFoundError(
                f"Qdrant storage not found: {QDRANT_PATH}"
            )

        self.client = QdrantClient(path=str(QDRANT_PATH))

        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.close()
            raise RuntimeError(
                f"Qdrant collection '{COLLECTION_NAME}' not found."
            )

        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve(self, question: str) -> list[dict]:
        """Retrieve and rerank relevant agricultural passages."""

        vector = self.embedding_model.encode(
            question,
            normalize_embeddings=True
        ).tolist()

        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=CANDIDATE_LIMIT,
            with_payload=True
        )

        results = []

        for point in response.points:
            payload = point.payload or {}
            passage = payload.get("text", "")
            semantic_score = float(point.score)

            hybrid_score = (
                0.70 * semantic_score
                + 0.30 * keyword_score(question, passage)
            )

            results.append({
                "score": hybrid_score,
                "semantic_score": semantic_score,
                "text": passage,
                "source": payload.get("source", "Unknown"),
                "page": payload.get("page", "Unknown")
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:TOP_K]

    def answer(self, question: str) -> dict:
        """Generate an answer and return the retrieved references."""

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        results = self.retrieve(question)

        if (
            not results
            or results[0]["score"] < MIN_RELEVANCE_SCORE
        ):
            return {
                "answer": (
                    "I could not find sufficiently relevant information "
                    "in the agricultural knowledge base to answer "
                    "that question reliably."
                ),
                "sources": [],
                "retrieval_status": "insufficient_relevance"
            }

        context_parts = []

        for index, result in enumerate(results, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"Document: {result['source']}\n"
                f"Page: {result['page']}\n"
                f"Passage: {result['text']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a careful agricultural research assistant.

Answer the farmer's question using only the reference passages below.

STRICT EVIDENCE RULES:
1. Use only facts supported by the reference passages.
2. Treat every crop and cropping system as distinct.
3. Before using a statistic, verify that it refers to the exact
   crop or cropping system being discussed.
4. Never present a result from one cropping system as a result
   for another cropping system.
5. If a passage compares two systems, explain the comparison
   accurately. Do not describe both values as benefits of the
   system in the farmer's question.
6. Do not infer that a system caused a higher yield unless the
   passage explicitly supports that conclusion.
7. Include statistics only when their meaning and context are clear.
8. If the evidence is ambiguous or insufficient, leave out the
   uncertain claim and explain the limitation.
9. Do not invent fertilizer doses, yields, percentages, or citations.
10. Cite only the document and page that support each factual claim.
11. Use simple language and distinguish research findings from
    general recommendations.
12. If the passages do not answer the question, say so clearly.
13. If the question is unrelated to agriculture, explain that the
    agricultural knowledge base does not cover it.

IMPORTANT:
A statistic about maize-wheat-greengram must not be presented as
a statistic about rice-wheat-greengram. A comparison with
pigeonpea-wheat does not establish the wheat yield of every other
cropping system.

REFERENCE PASSAGES:
{context}

FARMER'S QUESTION:
{question}

Write a concise answer. Include only conclusions that the passages
directly support. If a requested detail cannot be established,
state that limitation instead of guessing.
"""


        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )

        response.raise_for_status()

        
        answer_text = response.json()["response"].strip()

        # Detect when the model explicitly reports insufficient evidence.
        insufficient_phrases = [
            "do not provide",
            "does not provide",
            "do not contain",
            "does not contain",
            "cannot answer",
            "cannot directly answer",
            "not enough information",
            "insufficient information",
            "cannot be determined",
            "unable to answer"
        ]

        normalized_answer = answer_text.lower()

        evidence_insufficient = any(
            phrase in normalized_answer
            for phrase in insufficient_phrases
        )

        # Return source metadata separately so an API can expose it.
        sources = [
            {
                "document": result["source"],
                "page": result["page"],
                "score": round(result["score"], 4)
            }
            for result in results
        ]


        # Return source metadata separately so an API can expose it.
        sources = [
            {
                "document": result["source"],
                "page": result["page"],
                "score": round(result["score"], 4)
            }
            for result in results
        ]

        
        return {
            "answer": answer_text,
            "sources": sources,
            "retrieval_status": (
                "insufficient_evidence"
                if evidence_insufficient
                else "results_found"
            )
        }


    def close(self):
        self.client.close()
