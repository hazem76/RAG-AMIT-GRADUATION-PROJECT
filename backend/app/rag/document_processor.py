"""Document processing and text extraction."""
import os
import re
from typing import List, Tuple
from pathlib import Path
import PyPDF2
from docx import Document as DocxDocument
from app.core.config import settings


class DocumentProcessor:
    """Process and extract text from documents."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from various file formats."""
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.pdf':
            return DocumentProcessor._extract_pdf(file_path)
        elif file_ext == '.docx':
            return DocumentProcessor._extract_docx(file_path)
        elif file_ext == '.txt':
            return DocumentProcessor._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
        except Exception as e:
            raise ValueError(f"Error extracting PDF: {str(e)}")
        return "\n".join(text)

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """Extract text from DOCX."""
        text = []
        try:
            doc = DocxDocument(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)
        except Exception as e:
            raise ValueError(f"Error extracting DOCX: {str(e)}")
        return "\n".join(text)

    @staticmethod
    def _extract_txt(file_path: str) -> str:
        """Extract text from TXT."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error extracting TXT: {str(e)}")

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and preprocess text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', text)
        # Remove multiple consecutive punctuation
        text = re.sub(r'\.{2,}', '.', text)
        return text.strip()

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """Split text into overlapping chunks."""
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP

        # Clean text first
        text = DocumentProcessor.clean_text(text)

        # Split by sentences first for better semantic chunks
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                if chunk_text.strip():
                    chunks.append(chunk_text)

                # Keep overlap
                overlap_sentences = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    overlap_length += len(s) + 1
                    if overlap_length > chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)

                current_chunk = overlap_sentences
                current_length = overlap_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 1

        # Add last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)

        # Filter empty chunks
        chunks = [c for c in chunks if c.strip()]

        # If chunks are too small, try character-based chunking
        if not chunks:
            chunks = [
                text[i:i + chunk_size]
                for i in range(0, len(text), chunk_size - chunk_overlap)
            ]
            chunks = [c.strip() for c in chunks if c.strip()]

        return chunks

    @staticmethod
    def process_file(file_path: str) -> Tuple[List[str], int]:
        """Process a file and return chunks."""
        try:
            # Extract text
            raw_text = DocumentProcessor.extract_text(file_path)

            # Clean text
            cleaned_text = DocumentProcessor.clean_text(raw_text)

            # Chunk text
            chunks = DocumentProcessor.chunk_text(cleaned_text)

            return chunks, len(chunks)
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
