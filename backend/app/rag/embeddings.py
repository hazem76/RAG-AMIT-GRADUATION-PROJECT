"""Embeddings and vector database management."""
import os
import json
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from app.core.config import settings


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self):
        """Initialize embedding model and vector database."""
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="supportmind_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings

    def add_documents(
        self,
        document_id: int,
        chunks: List[str],
        metadatas: List[dict] = None
    ) -> List[str]:
        """Add document chunks to vector database."""
        if metadatas is None:
            metadatas = [{"document_id": str(document_id), "chunk_index": i} for i in range(len(chunks))]

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        # Create IDs
        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        return ids

    def retrieve_similar(
        self,
        query: str,
        top_k: int = None
    ) -> Tuple[List[str], List[float], List[dict]]:
        """Retrieve similar documents for a query."""
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if not results or not results.get('documents'):
            return [], [], []

        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []

        # Convert distances to similarity scores (cosine similarity)
        # ChromaDB returns distances, we convert to similarity (1 - distance)
        similarity_scores = [1 - d for d in distances]

        return documents, similarity_scores, metadatas

    def delete_document(self, document_id: int) -> None:
        """Delete all chunks for a document."""
        # Get all IDs for this document
        results = self.collection.get(
            where={"document_id": {"$eq": str(document_id)}}
        )
        if results['ids']:
            self.collection.delete(ids=results['ids'])

    def search(self, query: str, top_k: int = None) -> List[dict]:
        """Search for relevant chunks."""
        chunks, scores, metadatas = self.retrieve_similar(query, top_k)

        results = []
        for chunk, score, metadata in zip(chunks, scores, metadatas):
            results.append({
                "text": chunk,
                "score": float(score),
                "metadata": metadata
            })

        return results

    def clear_collection(self) -> None:
        """Clear all documents from collection."""
        self.client.delete_collection(name="supportmind_documents")
        self.collection = self.client.get_or_create_collection(
            name="supportmind_documents",
            metadata={"hnsw:space": "cosine"}
        )
