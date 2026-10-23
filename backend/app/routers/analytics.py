"""Analytics and dashboard routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.schemas import UserResponse, AnalyticsDashboard
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get dashboard metrics."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    metrics = AnalyticsService.get_dashboard_metrics(db)
    return AnalyticsDashboard(**metrics)


@router.get("/chat-analytics")
async def get_chat_analytics(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get chat analytics."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return AnalyticsService.get_chat_analytics(db, days)


@router.get("/ticket-analytics")
async def get_ticket_analytics(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get ticket analytics."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return AnalyticsService.get_ticket_analytics(db, days)


@router.get("/confidence-distribution")
async def get_confidence_distribution(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get confidence score distribution."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return AnalyticsService.get_confidence_distribution(db)


@router.get("/user-activity/{user_id}")
async def get_user_activity(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user activity metrics."""
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    return AnalyticsService.get_user_activity(db, user_id)
