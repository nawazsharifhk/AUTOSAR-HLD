import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database import crud
from backend.models.schemas import ExportRequest, AuditLogResponse
from backend.services.report_service import report_service

router = APIRouter(prefix="/api", tags=["Reports & Audit"])


@router.post("/export")
def export_architecture_report(request: ExportRequest, db: Session = Depends(get_db)):
    """
    Generate and export structured architecture report in PDF, Word, Excel, or JSON format.
    """
    try:
        report_info = report_service.generate_report(db, request)
        return {
            "status": "success",
            "message": f"Report generated successfully in {request.format.upper()} format.",
            "filename": report_info["filename"],
            "download_url": f"/api/reports/download/{report_info['filename']}",
            "stats": {
                "components": report_info["components_count"],
                "interfaces": report_info["interfaces_count"],
                "findings": report_info["findings_count"]
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


@router.get("/reports/download/{filename}")
def download_report(filename: str):
    """
    Download generated report file.
    """
    file_path = os.path.join("./data/reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested report file not found.")

    media_type = "application/octet-stream"
    if filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".json"):
        media_type = "application/json"

    return FileResponse(path=file_path, filename=filename, media_type=media_type)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_trail(limit: int = Query(default=100, le=500), db: Session = Depends(get_db)):
    """
    Retrieve system audit log trail for governance & compliance.
    """
    return crud.get_audit_logs(db, limit=limit)
