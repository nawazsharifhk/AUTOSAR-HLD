from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.schemas import RevisionComparisonRequest, RevisionComparisonResponse
from backend.services.comparison_service import comparison_service

router = APIRouter(prefix="/api/compare", tags=["Revision Comparison"])


@router.post("", response_model=RevisionComparisonResponse)
def compare_hld_revisions(request: RevisionComparisonRequest, db: Session = Depends(get_db)):
    """
    Compare two HLD document revisions (e.g. HLD v1.0 vs HLD v2.0).
    Returns added, removed, modified components & interfaces, and detected inconsistencies.
    """
    try:
        diff_report = comparison_service.compare_revisions(
            db=db,
            doc_v1_id=request.doc_v1_id,
            doc_v2_id=request.doc_v2_id
        )
        return diff_report
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")
