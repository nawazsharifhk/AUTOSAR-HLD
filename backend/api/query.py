from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.schemas import QueryRequest, QueryResponse
from backend.services.rag_service import rag_service

router = APIRouter(prefix="/api/query", tags=["RAG Q&A"])


@router.post("", response_model=QueryResponse)
def query_architecture(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Query the indexed AUTOSAR HLD documents using evidence-grounded RAG.
    Returns synthesized answer, page citations, confidence score, and limitation indicators.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = rag_service.answer_question(
            db=db,
            question=request.question,
            document_id=request.document_id,
            project_id=request.project_id or "default-project",
            top_k=request.top_k or 5
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")
