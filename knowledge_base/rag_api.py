
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from knowledge_base.scripts.rag_service import RAGService


rag_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service

    print("Starting Smart Agriculture RAG API...")
    rag_service = RAGService()
    print("RAG service initialized successfully.")

    yield

    if rag_service is not None:
        rag_service.close()
        print("RAG service stopped.")


app = FastAPI(
    title="Smart Agriculture RAG API",
    description=(
        "An agricultural question-answering API powered by "
        "Qdrant, Sentence Transformers, and Ollama."
    ),
    version="1.0.0",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The farmer's agricultural question"
    )


class Source(BaseModel):
    document: str
    page: str | int
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_status: str


@app.get("/")
def home():
    return {
        "message": "Smart Agriculture RAG API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Smart Agriculture RAG API",
        "knowledge_base": "agricultural_knowledge"
    }


@app.post("/rag/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not initialized."
        )

    try:
        result = rag_service.answer(request.question)

        return ChatResponse(**result)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        print(f"RAG request failed: {type(error).__name__}: {error}")

        raise HTTPException(
            status_code=500,
            detail="The agricultural assistant could not process the request."
        ) from error
