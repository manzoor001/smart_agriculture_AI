import json
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.security import get_current_user
from app.models.conversation import ChatConversation, ChatMessage
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["GenAI Chat"])

RAG_API_URL = "http://127.0.0.1:8001/rag/chat"


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", max_length=200)


class MessageCreate(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


def get_owned_conversation(
    conversation_id: int,
    user: User,
    db: Session,
) -> ChatConversation:
    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = ChatConversation(
        user_id=current_user.id,
        title=payload.title.strip() or "New conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
    }


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == current_user.id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_owned_conversation(
        conversation_id,
        current_user,
        db,
    )

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question cannot be empty",
        )

    # Call the existing Agricultural RAG API first.
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                RAG_API_URL,
                json={"question": question},
            )
            response.raise_for_status()
            result = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The agricultural AI service took too long to respond.",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The agricultural AI service returned an error.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to the Agricultural RAG service. Check that it is running on port 8001.",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The agricultural AI service returned an invalid response.",
        )

    answer = result.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The agricultural AI service did not return an answer.",
        )

    sources = result.get("sources", [])
    retrieval_status = result.get("retrieval_status")

    # Save both messages after the AI has returned a valid answer.
    try:
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )

        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            citations=json.dumps(sources, ensure_ascii=False),
            retrieval_status=(
                str(retrieval_status)
                if retrieval_status is not None
                else None
            ),
        )

        conversation.updated_at = datetime.now(timezone.utc)

        # Give a new conversation its first question as the title.
        if conversation.title == "New conversation":
            conversation.title = question[:200]

        db.add_all([user_message, assistant_message])
        db.commit()
        db.refresh(user_message)
        db.refresh(assistant_message)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The AI answered, but the conversation could not be saved.",
        )

    return {
        "conversation_id": conversation.id,
        "question": {
            "id": user_message.id,
            "role": user_message.role,
            "content": user_message.content,
            "created_at": user_message.created_at,
        },
        "answer": {
            "id": assistant_message.id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at,
        },
        "citations": sources,
        "retrieval_status": retrieval_status,
    }


@router.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_owned_conversation(
        conversation_id,
        current_user,
        db,
    )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.id.asc())
        .all()
    )

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "citations": (
                json.loads(message.citations)
                if message.citations
                else []
            ),
            "retrieval_status": message.retrieval_status,
            "created_at": message.created_at,
        }
        for message in messages
    ]
