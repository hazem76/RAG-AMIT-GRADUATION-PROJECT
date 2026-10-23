"""Ticket repository for database access."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Ticket


class TicketRepository:
    """Repository for ticket operations."""

    @staticmethod
    def create_ticket(
        db: Session,
        user_id: int,
        title: str,
        description: str,
        category: str,
        priority: str = "medium"
    ) -> Ticket:
        """Create new ticket."""
        ticket = Ticket(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Ticket:
        """Get ticket by ID."""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    @staticmethod
    def get_user_tickets(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get user's tickets."""
        return (
            db.query(Ticket)
            .filter(Ticket.user_id == user_id)
            .order_by(desc(Ticket.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, **kwargs) -> Ticket:
        """Update ticket."""
        ticket = TicketRepository.get_ticket(db, ticket_id)
        if ticket:
            for key, value in kwargs.items():
                if value is not None:
                    if key == "status" and value == "resolved":
                        ticket.resolved_at = datetime.utcnow()
                    setattr(ticket, key, value)
            db.commit()
            db.refresh(ticket)
        return ticket

    @staticmethod
    def get_all_tickets(db: Session, skip: int = 0, limit: int = 50):
        """Get all tickets."""
        return (
            db.query(Ticket)
            .order_by(desc(Ticket.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_tickets_by_status(db: Session, status: str):
        """Get tickets by status."""
        return db.query(Ticket).filter(Ticket.status == status).all()

    @staticmethod
    def get_ticket_count(db: Session) -> int:
        """Get total ticket count."""
        return db.query(Ticket).count()

    @staticmethod
    def get_open_ticket_count(db: Session) -> int:
        """Get open ticket count."""
        return db.query(Ticket).filter(Ticket.status == "open").count()
