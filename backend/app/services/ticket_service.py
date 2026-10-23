"""Ticket service for managing support tickets."""
from sqlalchemy.orm import Session
from app.repositories.ticket_repository import TicketRepository
from app.rag.gemini_integration import GeminiService
from app.services.lazy_services import get_embedding_service
from app.schemas.schemas import TicketCreate, TicketUpdate


class TicketService:
    """Service for ticket operations."""

    def __init__(self):
        """Initialize ticket service."""
        self.gemini_service = GeminiService()
        self.embedding_service = get_embedding_service()

    def create_ticket(
        self,
        db: Session,
        user_id: int,
        ticket_create: TicketCreate
    ):
        """Create new support ticket with AI analysis."""
        # Create ticket
        ticket = TicketRepository.create_ticket(
            db,
            user_id=user_id,
            title=ticket_create.title,
            description=ticket_create.description,
            category=ticket_create.category,
            priority=ticket_create.priority
        )

        # Generate AI summary
        summary = self.gemini_service.generate_ticket_summary(ticket_create.description)

        # Get relevant knowledge base docs for solution suggestion
        search_results = self.embedding_service.search(
            ticket_create.title + " " + ticket_create.description,
            top_k=3
        )
        context = [result['text'] for result in search_results]

        # Generate AI solution
        solution = self.gemini_service.generate_ticket_solution(
            ticket_create.description,
            context
        )

        # Update ticket with AI fields
        TicketRepository.update_ticket(
            db,
            ticket.id,
            ai_summary=summary,
            ai_solution=solution
        )

        # Refresh ticket
        ticket = TicketRepository.get_ticket(db, ticket.id)
        return ticket

    def update_ticket(
        self,
        db: Session,
        ticket_id: int,
        ticket_update: TicketUpdate
    ):
        """Update ticket."""
        update_data = ticket_update.model_dump(exclude_unset=True)
        return TicketRepository.update_ticket(db, ticket_id, **update_data)

    def get_ticket(self, db: Session, ticket_id: int):
        """Get ticket by ID."""
        return TicketRepository.get_ticket(db, ticket_id)

    def get_user_tickets(self, db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """Get user's tickets."""
        return TicketRepository.get_user_tickets(db, user_id, skip, limit)

    def get_all_tickets(self, db: Session, skip: int = 0, limit: int = 50):
        """Get all tickets (admin)."""
        return TicketRepository.get_all_tickets(db, skip, limit)

    def get_tickets_by_status(self, db: Session, status: str):
        """Get tickets by status."""
        return TicketRepository.get_tickets_by_status(db, status)

    def get_ticket_statistics(self, db: Session):
        """Get ticket statistics."""
        total = TicketRepository.get_ticket_count(db)
        open_count = TicketRepository.get_open_ticket_count(db)
        resolved = TicketRepository.get_tickets_by_status(db, "resolved")
        closed = TicketRepository.get_tickets_by_status(db, "closed")

        return {
            "total": total,
            "open": open_count,
            "resolved": len(resolved),
            "closed": len(closed),
            "resolution_rate": (len(resolved) + len(closed)) / total if total > 0 else 0
        }
