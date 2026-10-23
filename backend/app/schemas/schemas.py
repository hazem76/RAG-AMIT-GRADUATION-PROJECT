"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Chat Schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    confidence_score: Optional[float] = None
    citations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatDetailResponse(ChatResponse):
    messages: List[MessageResponse] = []


# Ticket Schemas
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(..., min_length=10)
    category: str = Field(..., pattern="^(billing|technical|general)$")
    priority: Optional[str] = "medium"


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    ai_summary: Optional[str] = None
    ai_solution: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    chunk_count: int
    is_processed: bool
    upload_date: datetime

    class Config:
        from_attributes = True


# RAG Schemas
class RAGResponse(BaseModel):
    answer: str
    confidence_score: float
    citations: List[dict] = []
    sources: List[str] = []
    retrieved_chunks: Optional[List[str]] = None


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = 5
    use_history: Optional[bool] = True


# Feedback Schemas
class FeedbackCreate(BaseModel):
    message_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class MetricResponse(BaseModel):
    metric_name: str
    metric_value: float
    metric_type: str
    recorded_at: datetime


class AnalyticsDashboard(BaseModel):
    total_chats: int
    total_tickets: int
    total_users: int
    avg_confidence_score: float
    avg_response_time: float
    user_satisfaction_score: float
    ticket_resolution_rate: float
