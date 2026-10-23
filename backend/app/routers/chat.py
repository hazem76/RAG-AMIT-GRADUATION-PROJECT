"""Chat routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    UserResponse, ChatCreate, ChatResponse, ChatDetailResponse,
    MessageCreate, MessageResponse, RAGQueryRequest, RAGResponse
)
from app.services.chat_service import ChatService
from app.services.lazy_services import get_rag_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def create_chat(
    chat_create: ChatCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create new chat session."""
    chat = ChatService.create_chat(db, current_user.id, chat_create.title)
    return ChatResponse.model_validate(chat)


@router.get("", response_model=List[ChatResponse])
async def get_chats(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's chats."""
    chats = ChatService.get_user_chats(db, current_user.id, skip, limit)
    return [ChatResponse.model_validate(chat) for chat in chats]


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get chat with messages."""
    chat = ChatService.get_chat_with_messages(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Check ownership
    chat_obj = db.query(__import__('app.models.models', fromlist=['Chat']).Chat).get(chat_id)
    if chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return ChatDetailResponse(
        id=chat["id"],
        title=chat["title"],
        created_at=chat["created_at"],
        updated_at=chat["updated_at"],
        messages=[MessageResponse.model_validate(m) for m in chat["messages"]]
    )


@router.post("/{chat_id}/message", response_model=RAGResponse)
async def send_message(
    chat_id: int,
    message_request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Send message and get AI response."""
    # Verify chat ownership
    chat_obj = db.query(__import__('app.models.models', fromlist=['Chat']).Chat).get(chat_id)
    if not chat_obj or chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Add user message
    ChatService.add_user_message(db, chat_id, message_request.query)

    # Get conversation history
    history = ChatService.get_conversation_history(db, chat_id)

    # Generate AI response
    response = get_rag_service().retrieve_and_generate_response(
        message_request.query,
        history,
        message_request.top_k
    )

    # Add assistant message
    ChatService.add_assistant_message(
        db,
        chat_id,
        response["answer"],
        response.get("confidence_score", 0),
        response.get("citations", [])
    )

    return RAGResponse(**response)


@router.put("/{chat_id}/title")
async def update_chat_title(
    chat_id: int,
    new_title: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update chat title."""
    # Verify chat ownership
    chat_obj = db.query(__import__('app.models.models', fromlist=['Chat']).Chat).get(chat_id)
    if not chat_obj or chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    chat = ChatService.update_chat_title(db, chat_id, new_title)
    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a chat."""
    # Verify chat ownership
    chat_obj = db.query(__import__('app.models.models', fromlist=['Chat']).Chat).get(chat_id)
    if not chat_obj or chat_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    ChatService.delete_chat(db, chat_id)
    return {"message": "Chat deleted successfully"}
