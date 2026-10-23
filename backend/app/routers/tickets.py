"""Ticket management routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    UserResponse, TicketCreate, TicketUpdate, TicketResponse
)
from app.services.lazy_services import get_ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse)
async def create_ticket(
    ticket_create: TicketCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create new support ticket."""
    ticket = get_ticket_service().create_ticket(db, current_user.id, ticket_create)
    return TicketResponse.model_validate(ticket)


@router.get("", response_model=List[TicketResponse])
async def get_tickets(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's tickets."""
    tickets = get_ticket_service().get_user_tickets(db, current_user.id, skip, limit)
    return [TicketResponse.model_validate(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get ticket details."""
    ticket = get_ticket_service().get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check ownership (admin can view all)
    if ticket.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    return TicketResponse.model_validate(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update ticket."""
    ticket = get_ticket_service().get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check ownership (admin can update all)
    if ticket.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    updated_ticket = get_ticket_service().update_ticket(db, ticket_id, ticket_update)
    return TicketResponse.model_validate(updated_ticket)


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete ticket (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = get_ticket_service().get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Delete through database
    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}


@router.get("/admin/all", response_model=List[TicketResponse])
async def get_all_tickets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all tickets (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    tickets = get_ticket_service().get_all_tickets(db, skip, limit)
    return [TicketResponse.model_validate(t) for t in tickets]
