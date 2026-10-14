from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models.db_models import (
    DocumentModel,
    DocumentChunkModel,
    ComponentModel,
    InterfaceModel,
    FindingModel,
    AuditLogModel
)
from backend.models.schemas import (
    ComponentBase,
    InterfaceBase,
    FindingCreate,
    FindingUpdate
)


# Document operations
def create_document(db: Session, name: str, version: str, project_id: str, uploaded_by: str, file_path: str, page_count: int, summary: str = "") -> DocumentModel:
    doc = DocumentModel(
        name=name,
        version=version,
        project_id=project_id,
        uploaded_by=uploaded_by,
        file_path=file_path,
        page_count=page_count,
        summary=summary,
        status="Processed"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_documents(db: Session, project_id: Optional[str] = None) -> List[DocumentModel]:
    query = db.query(DocumentModel)
    if project_id:
        query = query.filter(DocumentModel.project_id == project_id)
    return query.order_by(DocumentModel.upload_date.desc()).all()


def get_document_by_id(db: Session, document_id: int) -> Optional[DocumentModel]:
    return db.query(DocumentModel).filter(DocumentModel.id == document_id).first()


def delete_document(db: Session, document_id: int) -> bool:
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


# Chunk operations
def create_document_chunks(db: Session, chunks_data: List[Dict[str, Any]]) -> List[DocumentChunkModel]:
    chunk_models = []
    for c in chunks_data:
        chunk = DocumentChunkModel(
            document_id=c["document_id"],
            page=c["page"],
            section=c.get("section", ""),
            component=c.get("component", ""),
            text=c["text"],
            embedding_id=c.get("embedding_id")
        )
        chunk_models.append(chunk)
    db.add_all(chunk_models)
    db.commit()
    return chunk_models


def get_chunks_by_document(db: Session, document_id: int) -> List[DocumentChunkModel]:
    return db.query(DocumentChunkModel).filter(DocumentChunkModel.document_id == document_id).all()


# Component operations
def create_components(db: Session, document_id: int, components: List[ComponentBase]) -> List[ComponentModel]:
    comp_models = []
    for c in components:
        comp = ComponentModel(
            document_id=document_id,
            name=c.name,
            type=c.type,
            description=c.description,
            page=c.page,
            ports_in=c.ports_in or [],
            ports_out=c.ports_out or [],
            asil_level=c.asil_level or "ASIL-B"
        )
        comp_models.append(comp)
    db.add_all(comp_models)
    db.commit()
    return comp_models


def get_components_by_document(db: Session, document_id: int) -> List[ComponentModel]:
    return db.query(ComponentModel).filter(ComponentModel.document_id == document_id).all()


# Interface operations
def create_interfaces(db: Session, document_id: int, interfaces: List[InterfaceBase]) -> List[InterfaceModel]:
    iface_models = []
    for iface in interfaces:
        model = InterfaceModel(
            document_id=document_id,
            name=iface.name,
            source=iface.source,
            target=iface.target,
            description=iface.description,
            page=iface.page,
            interface_type=iface.interface_type or "Sender-Receiver",
            signals=iface.signals or []
        )
        iface_models.append(model)
    db.add_all(iface_models)
    db.commit()
    return iface_models


def get_interfaces_by_document(db: Session, document_id: int) -> List[InterfaceModel]:
    return db.query(InterfaceModel).filter(InterfaceModel.document_id == document_id).all()


# Finding operations (Human-in-the-Loop)
def create_findings(db: Session, findings: List[FindingCreate]) -> List[FindingModel]:
    finding_models = []
    for f in findings:
        model = FindingModel(
            document_id=f.document_id,
            type=f.type,
            description=f.description,
            evidence=f.evidence,
            confidence=f.confidence,
            status=f.status,
            reviewer=f.reviewer,
            review_notes=f.review_notes
        )
        finding_models.append(model)
    db.add_all(finding_models)
    db.commit()
    return finding_models


def get_findings_by_document(db: Session, document_id: Optional[int] = None) -> List[FindingModel]:
    query = db.query(FindingModel)
    if document_id:
        query = query.filter(FindingModel.document_id == document_id)
    return query.order_by(FindingModel.created_at.desc()).all()


def update_finding(db: Session, finding_id: int, update_data: FindingUpdate) -> Optional[FindingModel]:
    finding = db.query(FindingModel).filter(FindingModel.id == finding_id).first()
    if finding:
        finding.status = update_data.status
        finding.reviewer = update_data.reviewer or finding.reviewer
        finding.review_notes = update_data.review_notes or finding.review_notes
        db.commit()
        db.refresh(finding)
    return finding


# Audit log operations
def create_audit_log(db: Session, user: str, action: str, document: str, result: str, details: str = "") -> AuditLogModel:
    log = AuditLogModel(
        user=user,
        action=action,
        document=document,
        result=result,
        details=details
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(db: Session, limit: int = 100) -> List[AuditLogModel]:
    return db.query(AuditLogModel).order_by(AuditLogModel.timestamp.desc()).limit(limit).all()
