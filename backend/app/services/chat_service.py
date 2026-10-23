"""Chat service for managing conversations."""
import json
from sqlalchemy.orm import Session
from app.repositories.chat_repository import ChatRepository
from app.schemas.schemas import MessageResponse


class ChatService:
    """Service for chat operations."""

    @staticmethod
    def create_chat(db: Session, user_id: int, title: str = "New Chat"):
        """Create new chat session."""
        return ChatRepository.create_chat(db, user_id, title)

    @staticmethod
    def get_chat_with_messages(db: Session, chat_id: int):
        """Get chat with all messages."""
        chat = ChatRepository.get_chat(db, chat_id)
        if not chat:
            return None

        messages = ChatRepository.get_chat_messages(db, chat_id)
        return {
            "id": chat.id,
            "title": chat.title,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "messages": messages
        }

    @staticmethod
    def add_user_message(db: Session, chat_id: int, content: str) -> MessageResponse:
        """Add user message to chat."""
        message = ChatRepository.add_message(db, chat_id, "user", content)
        return MessageResponse.model_validate(message)

    @staticmethod
    def add_assistant_message(
        db: Session,
        chat_id: int,
        content: str,
        confidence_score: float = None,
        citations: list = None
    ) -> MessageResponse:
        """Add assistant message to chat."""
        citations_json = json.dumps(citations) if citations else None
        message = ChatRepository.add_message(
            db,
            chat_id,
            "assistant",
            content,
            confidence_score=confidence_score,
            citations=citations_json
        )
        return MessageResponse.model_validate(message)

    @staticmethod
    def get_user_chats(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get user's chat sessions."""
        return ChatRepository.get_user_chats(db, user_id, skip, limit)

    @staticmethod
    def update_chat_title(db: Session, chat_id: int, title: str):
        """Update chat title."""
        return ChatRepository.update_chat_title(db, chat_id, title)

    @staticmethod
    def delete_chat(db: Session, chat_id: int) -> bool:
        """Delete a chat."""
        return ChatRepository.delete_chat(db, chat_id)

    @staticmethod
    def get_conversation_history(db: Session, chat_id: int) -> list:
        """Get conversation history for context."""
        messages = ChatRepository.get_chat_messages(db, chat_id)
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        return history
