"""Authentication service."""
from datetime import timedelta
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate, LoginRequest, TokenResponse, UserResponse


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register(db: Session, user_create: UserCreate) -> TokenResponse:
        """Register new user."""
        # Check if user exists
        existing_user = UserRepository.get_user_by_email(db, user_create.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Create user
        user = UserRepository.create_user(
            db,
            name=user_create.name,
            email=user_create.email,
            password=user_create.password
        )

        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=30)
        )

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def login(db: Session, login_request: LoginRequest) -> TokenResponse:
        """Login user."""
        user = UserRepository.authenticate_user(
            db,
            login_request.email,
            login_request.password
        )
        if not user:
            raise ValueError("Invalid email or password")

        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=30)
        )

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def get_current_user(db: Session, user_id: int) -> UserResponse:
        """Get current user by ID."""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
