
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

router = APIRouter(
    prefix="/rag",
    tags=["Agricultural AI Assistant"]
)

RAG_API_URL = "http://127.0.0.1:8001/rag/chat"


class RAGChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Ask an agricultural question"
    )


@router.post("/chat")
async def chat_with_agricultural_ai(request: RAGChatRequest):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                RAG_API_URL,
                json={"question": request.question}
            )

            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="The agricultural AI assistant took too long to respond."
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The RAG service returned an error."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail=(
                "The RAG service is unavailable. "
                "Please ensure the RAG API is running on port 8001."
            )
        )
