"""Chat repository for database access."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Chat, Message


class ChatRepository:
    """Repository for chat operations."""

    @staticmethod
    def create_chat(db: Session, user_id: int, title: str = "New Chat") -> Chat:
        """Create new chat."""
        chat = Chat(user_id=user_id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_chat(db: Session, chat_id: int) -> Chat:
        """Get chat by ID."""
        return db.query(Chat).filter(Chat.id == chat_id).first()

    @staticmethod
    def get_user_chats(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get user's chats."""
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(desc(Chat.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def add_message(
        db: Session,
        chat_id: int,
        role: str,
        content: str,
        confidence_score: float = None,
        citations: str = None
    ) -> Message:
        """Add message to chat."""
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            confidence_score=confidence_score,
            citations=citations
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_chat_messages(db: Session, chat_id: int):
        """Get all messages in a chat."""
        return db.query(Message).filter(Message.chat_id == chat_id).all()

    @staticmethod
    def delete_chat(db: Session, chat_id: int) -> bool:
        """Delete a chat."""
        chat = ChatRepository.get_chat(db, chat_id)
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False

    @staticmethod
    def update_chat_title(db: Session, chat_id: int, title: str) -> Chat:
        """Update chat title."""
        chat = ChatRepository.get_chat(db, chat_id)
        if chat:
            chat.title = title
            db.commit()
            db.refresh(chat)
        return chat

    @staticmethod
    def get_chat_count(db: Session, user_id: int) -> int:
        """Get user's chat count."""
        return db.query(Chat).filter(Chat.user_id == user_id).count()
