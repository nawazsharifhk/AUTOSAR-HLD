from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0")
    project_id = Column(String(100), default="default-project", index=True)
    uploaded_by = Column(String(100), default="Lead Automotive Architect")
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Processed")  # Uploaded, Processing, Processed, Error
    file_path = Column(String(500), nullable=False)
    page_count = Column(Integer, default=1)
    summary = Column(Text, nullable=True)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")
    components = relationship("ComponentModel", back_populates="document", cascade="all, delete-orphan")
    interfaces = relationship("InterfaceModel", back_populates="document", cascade="all, delete-orphan")
    findings = relationship("FindingModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page = Column(Integer, nullable=False)
    section = Column(String(255), nullable=True)
    component = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=True)

    document = relationship("DocumentModel", back_populates="chunks")


class ComponentModel(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), default="Software Component")
    description = Column(Text, nullable=True)
    page = Column(Integer, default=1)
    ports_in = Column(JSON, default=list)
    ports_out = Column(JSON, default=list)
    asil_level = Column(String(50), default="ASIL-B")

    document = relationship("DocumentModel", back_populates="components")


class InterfaceModel(Base):
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    target = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    page = Column(Integer, default=1)
    interface_type = Column(String(100), default="Sender-Receiver")
    signals = Column(JSON, default=list)

    document = relationship("DocumentModel", back_populates="interfaces")


class FindingModel(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)  # Inconsistency, Missing Dependency, Architecture Violation, Terminology Issue
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    confidence = Column(Float, default=0.85)
    status = Column(String(100), default="Requires Engineer Review")  # Requires Engineer Review, Accepted, Rejected, Edited
    reviewer = Column(String(100), default="Pending")
    review_notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("DocumentModel", back_populates="findings")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    document = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    result = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
