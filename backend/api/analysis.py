from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database import crud
from backend.models.schemas import (
    ArchitectureAnalysisResponse,
    ComponentResponse,
    InterfaceResponse,
    FindingResponse,
    FindingUpdate,
    ComponentBase,
    InterfaceBase
)
from backend.utils.graph_builder import graph_builder

router = APIRouter(prefix="/api/analysis", tags=["Architecture Analysis"])


@router.get("/document/{document_id}", response_model=ArchitectureAnalysisResponse)
def get_document_architecture(document_id: int, db: Session = Depends(get_db)):
    """
    Retrieve extracted components, interfaces, dependencies, and findings for a document.
    """
    doc = crud.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    comps = crud.get_components_by_document(db, document_id)
    ifaces = crud.get_interfaces_by_document(db, document_id)
    findings = crud.get_findings_by_document(db, document_id)

    comp_bases = [
        ComponentBase(
            name=c.name,
            type=c.type,
            description=c.description,
            page=c.page,
            ports_in=c.ports_in or [],
            ports_out=c.ports_out or [],
            asil_level=c.asil_level or "ASIL-B"
        ) for c in comps
    ]

    iface_bases = [
        InterfaceBase(
            name=i.name,
            source=i.source,
            target=i.target,
            description=i.description,
            page=i.page,
            interface_type=i.interface_type,
            signals=i.signals or []
        ) for i in ifaces
    ]

    dependencies = [
        {
            "from_component": i.source,
            "to_component": i.target,
            "interface": i.name,
            "type": i.interface_type
        } for i in ifaces
    ]

    return ArchitectureAnalysisResponse(
        document_id=doc.id,
        document_name=doc.name,
        version=doc.version,
        components=comp_bases,
        interfaces=iface_bases,
        dependencies=dependencies,
        functional_flows=[],
        findings=findings
    )


@router.get("/document/{document_id}/graph")
def get_document_graph(document_id: int, db: Session = Depends(get_db)):
    """
    Build and return NetworkX architecture graph nodes and edges for visualization.
    """
    comps = crud.get_components_by_document(db, document_id)
    ifaces = crud.get_interfaces_by_document(db, document_id)
    return graph_builder.build_graph(comps, ifaces)


@router.get("/findings", response_model=List[FindingResponse])
def get_all_findings(document_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    List AI-detected architectural inconsistencies and findings for review.
    """
    return crud.get_findings_by_document(db, document_id)


@router.put("/findings/{finding_id}", response_model=FindingResponse)
def review_finding(
    finding_id: int,
    update_data: FindingUpdate,
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop review endpoint: Accept, Reject, or Edit AI finding.
    """
    finding = crud.update_finding(db, finding_id, update_data)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    crud.create_audit_log(
        db=db,
        user=update_data.reviewer or "Engineer",
        action="Human Review Finding",
        document=f"Finding #{finding.id}",
        result=f"Status set to {update_data.status}",
        details=f"Notes: {update_data.review_notes}"
    )

    return finding
