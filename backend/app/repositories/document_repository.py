"""Document repository for database access."""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Document, EmbeddingMetadata


class DocumentRepository:
    """Repository for document operations."""

    @staticmethod
    def create_document(
        db: Session,
        filename: str,
        file_type: str,
        file_path: str,
        uploaded_by: int = None
    ) -> Document:
        """Create new document."""
        doc = Document(
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            uploaded_by=uploaded_by
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_document(db: Session, doc_id: int) -> Document:
        """Get document by ID."""
        return db.query(Document).filter(Document.id == doc_id).first()

    @staticmethod
    def get_all_documents(db: Session, skip: int = 0, limit: int = 50):
        """Get all documents."""
        return (
            db.query(Document)
            .order_by(desc(Document.upload_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_document(db: Session, doc_id: int, **kwargs) -> Document:
        """Update document."""
        doc = DocumentRepository.get_document(db, doc_id)
        if doc:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(doc, key, value)
            db.commit()
            db.refresh(doc)
        return doc

    @staticmethod
    def delete_document(db: Session, doc_id: int) -> bool:
        """Delete a document."""
        doc = DocumentRepository.get_document(db, doc_id)
        if doc:
            db.delete(doc)
            db.commit()
            return True
        return False

    @staticmethod
    def add_embeddings(
        db: Session,
        doc_id: int,
        chunk_texts: list,
        vector_ids: list
    ) -> list:
        """Add embeddings for a document."""
        embeddings = []
        for i, (chunk_text, vector_id) in enumerate(zip(chunk_texts, vector_ids)):
            embedding = EmbeddingMetadata(
                document_id=doc_id,
                chunk_index=i,
                chunk_text=chunk_text,
                vector_id=vector_id
            )
            embeddings.append(embedding)
        db.add_all(embeddings)
        db.commit()
        return embeddings

    @staticmethod
    def get_document_embeddings(db: Session, doc_id: int):
        """Get all embeddings for a document."""
        return db.query(EmbeddingMetadata).filter(
            EmbeddingMetadata.document_id == doc_id
        ).all()

    @staticmethod
    def get_document_count(db: Session) -> int:
        """Get total document count."""
        return db.query(Document).count()
