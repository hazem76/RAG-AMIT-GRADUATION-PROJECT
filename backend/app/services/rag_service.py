"""RAG service for document management and retrieval."""
import os
from sqlalchemy.orm import Session
from app.services.lazy_services import get_embedding_service
from app.rag.document_processor import DocumentProcessor
from app.rag.gemini_integration import GeminiService
from app.repositories.document_repository import DocumentRepository
from app.core.config import settings


class RAGService:
    """Service for RAG operations."""

    def __init__(self):
        """Initialize RAG service."""
        self.embedding_service = get_embedding_service()
        self.gemini_service = GeminiService()

    def upload_document(
        self,
        db: Session,
        file_path: str,
        filename: str,
        file_type: str,
        user_id: int = None
    ):
        """Upload and process a document."""
        try:
            # Create document record
            document = DocumentRepository.create_document(
                db,
                filename=filename,
                file_type=file_type,
                file_path=file_path,
                uploaded_by=user_id
            )

            # Process document
            chunks, chunk_count = DocumentProcessor.process_file(file_path)

            if not chunks:
                raise ValueError("No text could be extracted from document")

            # Generate embeddings and add to vector DB
            vector_ids = self.embedding_service.add_documents(
                document.id,
                chunks,
                metadatas=[
                    {
                        "document_id": str(document.id),
                        "filename": filename,
                        "chunk_index": i
                    }
                    for i in range(len(chunks))
                ]
            )

            # Update document with embeddings
            DocumentRepository.add_embeddings(db, document.id, chunks, vector_ids)
            DocumentRepository.update_document(
                db,
                document.id,
                chunk_count=chunk_count,
                is_processed=True
            )

            return document

        except Exception as e:
            # Clean up if failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Error processing document: {str(e)}")

    def retrieve_and_generate_response(
        self,
        query: str,
        chat_history: list = None,
        top_k: int = None
    ) -> dict:
        """Retrieve relevant documents and generate response."""
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        try:
            # Retrieve relevant documents
            search_results = self.embedding_service.search(query, top_k)

            if not search_results:
                return {
                    "answer": "I don't have enough information in the knowledge base to answer this question. Please contact our support team.",
                    "confidence_score": 0.0,
                    "citations": [],
                    "sources": [],
                    "retrieved_chunks": []
                }

            # Extract context from search results
            context = [result['text'] for result in search_results]

            # Generate response using Gemini
            response = self.gemini_service.generate_response(
                query,
                context,
                chat_history
            )

            return response

        except Exception as e:
            return {
                "answer": f"Error generating response: {str(e)}",
                "confidence_score": 0.0,
                "citations": [],
                "sources": [],
                "error": str(e)
            }

    def delete_document(self, db: Session, doc_id: int):
        """Delete a document and its embeddings."""
        # Delete from vector DB
        self.embedding_service.delete_document(doc_id)

        # Delete from database
        document = DocumentRepository.get_document(db, doc_id)
        if document:
            # Delete file
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            DocumentRepository.delete_document(db, doc_id)

    def get_document_info(self, db: Session, doc_id: int):
        """Get document information."""
        return DocumentRepository.get_document(db, doc_id)

    def list_documents(self, db: Session, skip: int = 0, limit: int = 50):
        """List all documents."""
        return DocumentRepository.get_all_documents(db, skip, limit)

    def search_documents(self, query: str, top_k: int = None):
        """Search documents."""
        return self.embedding_service.search(query, top_k)
