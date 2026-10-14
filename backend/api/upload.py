import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database import crud
from backend.services.document_service import document_service
from backend.models.schemas import DocumentResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "./data/documents"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_hld_document(
    file: UploadFile = File(...),
    version: str = Form("1.0"),
    project_id: str = Form("default-project"),
    uploaded_by: str = Form("Lead Automotive Architect"),
    db: Session = Depends(get_db)
):
    """
    Upload an AUTOSAR HLD PDF document, parse pages, extract architecture entities,
    generate embeddings, and store in vector DB & SQLite.
    """
    if not file.filename.lower().endswith((".pdf", ".txt", ".md")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, TXT, and Markdown files are currently supported."
        )

    saved_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = document_service.process_and_index_pdf(
            db=db,
            file_path=saved_path,
            filename=file.filename,
            version=version,
            project_id=project_id,
            uploaded_by=uploaded_by
        )
        return {
            "status": "success",
            "message": f"Document '{file.filename}' successfully processed and indexed.",
            "document_id": result["document"].id,
            "document_name": result["document"].name,
            "version": result["document"].version,
            "page_count": result["page_count"],
            "chunk_count": result["chunk_count"],
            "components_count": result["components_count"],
            "interfaces_count": result["interfaces_count"],
            "findings_count": result["findings_count"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing document: {str(e)}"
        )


@router.get("", response_model=List[DocumentResponse])
def list_documents(project_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List all indexed documents in the workspace."""
    return crud.get_documents(db, project_id=project_id)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get single document metadata."""
    doc = crud.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete document, its entities, and its vector embeddings."""
    success = crud.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "success", "message": f"Document {document_id} deleted."}
