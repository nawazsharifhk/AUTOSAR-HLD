import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.rag.ingestion import extract_pages_from_pdf
from backend.rag.chunking import chunk_document_pages
from backend.rag.vector_store import vector_store
from backend.services.extraction_service import extraction_service
from backend.database import crud
from backend.models.schemas import DocumentResponse


class DocumentService:
    def __init__(self, upload_dir: str = "./data/documents"):
        self.upload_dir = upload_dir
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def process_and_index_pdf(
        self,
        db: Session,
        file_path: str,
        filename: str,
        version: str = "1.0",
        project_id: str = "default-project",
        uploaded_by: str = "Lead Automotive Architect"
    ) -> Dict[str, Any]:
        """
        1. Ingest PDF & extract pages/tables/text
        2. Create Document record in DB
        3. Create context-aware chunks & persist in ChromaDB & DB
        4. Extract components, interfaces, dependencies & findings
        5. Log audit trail
        """
        # Step 1: Extract pages
        pages_data = extract_pages_from_pdf(file_path)
        page_count = len(pages_data)
        full_text = "\n\n".join([p["text"] for p in pages_data])

        # Step 2: Create DB Document
        doc_record = crud.create_document(
            db=db,
            name=filename,
            version=version,
            project_id=project_id,
            uploaded_by=uploaded_by,
            file_path=file_path,
            page_count=page_count,
            summary=f"AUTOSAR High-Level Design document comprising {page_count} pages with architecture specifications."
        )

        # Step 3: Chunking & Vector Store Indexing
        chunks = chunk_document_pages(pages_data)
        collection_name = f"proj_{project_id}"

        # Add chunk metadata with doc ID
        for c in chunks:
            c["document_id"] = doc_record.id

        chunk_ids = vector_store.add_chunks(
            collection_name=collection_name,
            chunks=chunks,
            document_id=doc_record.id,
            document_name=filename
        )

        for idx, c in enumerate(chunks):
            c["embedding_id"] = chunk_ids[idx] if idx < len(chunk_ids) else f"chunk_{idx}"

        crud.create_document_chunks(db, chunks)

        # Step 4: Extract Architecture (Components, Interfaces, Inconsistencies)
        extraction_res = extraction_service.extract_architecture(
            document_id=doc_record.id,
            full_text=full_text,
            pages_data=pages_data
        )

        components = extraction_res["components"]
        interfaces = extraction_res["interfaces"]
        findings = extraction_res["findings"]

        crud.create_components(db, doc_record.id, components)
        crud.create_interfaces(db, doc_record.id, interfaces)
        crud.create_findings(db, findings)

        # Step 5: Audit Log
        crud.create_audit_log(
            db=db,
            user=uploaded_by,
            action="Document Ingestion & Indexing",
            document=filename,
            result="Success",
            details=f"Indexed {page_count} pages, {len(chunks)} chunks, {len(components)} SWCs, {len(interfaces)} interfaces, {len(findings)} findings."
        )

        return {
            "document": doc_record,
            "page_count": page_count,
            "chunk_count": len(chunks),
            "components_count": len(components),
            "interfaces_count": len(interfaces),
            "findings_count": len(findings)
        }


document_service = DocumentService()
