"""Lazy-loaded shared services to keep API startup fast."""

_embedding_service = None
_rag_service = None
_ticket_service = None


def get_embedding_service():
    """Load the embedding model only when first needed."""
    global _embedding_service
    if _embedding_service is None:
        from app.rag.embeddings import EmbeddingService

        _embedding_service = EmbeddingService()
    return _embedding_service


def get_rag_service():
    """Load RAG service only when first needed."""
    global _rag_service
    if _rag_service is None:
        from app.services.rag_service import RAGService

        _rag_service = RAGService()
    return _rag_service


def get_ticket_service():
    """Load ticket service only when first needed."""
    global _ticket_service
    if _ticket_service is None:
        from app.services.ticket_service import TicketService

        _ticket_service = TicketService()
    return _ticket_service
