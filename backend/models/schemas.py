from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ComponentBase(BaseModel):
    name: str
    type: str = "Software Component"  # e.g., Application SWC, Sensor SWC, Actuator SWC, BSW
    description: Optional[str] = ""
    page: Optional[int] = 1
    ports_in: Optional[List[str]] = []
    ports_out: Optional[List[str]] = []
    asil_level: Optional[str] = "ASIL-B"


class ComponentCreate(ComponentBase):
    document_id: int


class ComponentResponse(ComponentBase):
    id: int
    document_id: int
    model_config = ConfigDict(from_attributes=True)


class InterfaceBase(BaseModel):
    name: str
    source: str
    target: str
    description: Optional[str] = ""
    page: Optional[int] = 1
    interface_type: Optional[str] = "Sender-Receiver"  # Sender-Receiver, Client-Server
    signals: Optional[List[str]] = []


class InterfaceCreate(InterfaceBase):
    document_id: int


class InterfaceResponse(InterfaceBase):
    id: int
    document_id: int
    source_component: Optional[str] = None
    target_component: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class FindingBase(BaseModel):
    document_id: int
    type: str  # Inconsistency, Missing Dependency, Architecture Violation, Terminology Issue
    description: str
    evidence: str
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    status: str = "Requires Engineer Review"  # Requires Engineer Review, Accepted, Rejected, Edited
    reviewer: Optional[str] = "Pending"
    review_notes: Optional[str] = ""


class FindingCreate(FindingBase):
    pass


class FindingUpdate(BaseModel):
    status: str  # Accepted, Rejected, Edited
    reviewer: Optional[str] = "Engineer"
    review_notes: Optional[str] = ""


class FindingResponse(FindingBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    page: int
    section: Optional[str] = ""
    component: Optional[str] = ""
    text: str
    embedding_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: int
    name: str
    version: str
    project_id: str
    uploaded_by: str
    upload_date: datetime
    status: str
    page_count: int
    summary: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)


class Citation(BaseModel):
    page: int
    section: Optional[str] = ""
    excerpt: str
    document_name: Optional[str] = ""
    score: Optional[float] = 0.0


class QueryRequest(BaseModel):
    question: str
    document_id: Optional[int] = None
    project_id: Optional[str] = "default-project"
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    confidence: float
    limitation_indicator: Optional[str] = None
    is_inferred: bool = False
    evidence_found: bool = True


class ArchitectureAnalysisResponse(BaseModel):
    document_id: int
    document_name: str
    version: str
    components: List[ComponentBase]
    interfaces: List[InterfaceBase]
    dependencies: List[Dict[str, Any]] = []
    functional_flows: List[Dict[str, Any]] = []
    findings: List[FindingResponse] = []


class RevisionComparisonRequest(BaseModel):
    doc_v1_id: int
    doc_v2_id: int


class RevisionComparisonResponse(BaseModel):
    doc_v1_name: str
    doc_v1_version: str
    doc_v2_name: str
    doc_v2_version: str
    added_components: List[ComponentBase]
    removed_components: List[ComponentBase]
    modified_components: List[Dict[str, Any]]
    added_interfaces: List[InterfaceBase]
    removed_interfaces: List[InterfaceBase]
    modified_interfaces: List[Dict[str, Any]]
    inconsistencies: List[Dict[str, Any]]
    summary: str


class AuditLogResponse(BaseModel):
    id: int
    user: str
    action: str
    document: str
    timestamp: datetime
    result: str
    details: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    document_id: int
    format: str = "pdf"  # pdf, docx, excel, json
    include_findings: bool = True
    include_graph: bool = True
