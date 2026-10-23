"""Knowledge base document management routes."""
import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.routers.auth import get_current_user
from app.schemas.schemas import UserResponse, DocumentResponse
from app.services.lazy_services import get_rag_service

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])


def _ensure_upload_dir():
    """Ensure upload directory exists."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload knowledge base document."""
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower().strip(".")
    if file_ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(settings.allowed_file_types)}"
        )

    try:
        # Create upload directory
        _ensure_upload_dir()

        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            if len(contents) > settings.MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="File too large")
            f.write(contents)

        # Process document
        document = get_rag_service().upload_document(
            db,
            file_path,
            file.filename,
            file_ext,
            current_user.id
        )

        return DocumentResponse.model_validate(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List knowledge base documents."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    documents = get_rag_service().list_documents(db, skip, limit)
    return [DocumentResponse.model_validate(d) for d in documents]


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete document."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        get_rag_service().delete_document(db, doc_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}")
async def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document info."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    doc = get_rag_service().get_document_info(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse.model_validate(doc)


@router.post("/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Search documents."""
    try:
        results = get_rag_service().search_documents(query, top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
