"""User repository for database access."""
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import hash_password, verify_password


class UserRepository:
    """Repository for user operations."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, name: str, email: str, password: str, role: str = "user") -> User:
        """Create new user."""
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user."""
        user = UserRepository.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> User:
        """Update user."""
        user = UserRepository.get_user_by_id(db, user_id)
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 10):
        """List users."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_count(db: Session) -> int:
        """Get total user count."""
        return db.query(User).count()
