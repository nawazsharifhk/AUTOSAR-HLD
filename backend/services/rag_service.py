from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.rag.retriever import retriever
from backend.rag.prompts import AUTOSAR_RAG_SYSTEM_PROMPT
from backend.services.llm_service import llm_service
from backend.models.schemas import QueryResponse, Citation
from backend.database import crud


class RAGService:
    def answer_question(
        self,
        db: Session,
        question: str,
        document_id: Optional[int] = None,
        project_id: str = "default-project",
        top_k: int = 5,
        user: str = "Automotive Engineer"
    ) -> QueryResponse:
        """
        1. Retrieve relevant evidence chunks with citations
        2. Synthesize grounded answer strictly using retrieved context
        3. Evaluate confidence and limitation indicators
        4. Log audit trail
        """
        collection_name = f"proj_{project_id}"
        retrieval_res = retriever.retrieve(
            query=question,
            document_id=document_id,
            top_k=top_k,
            collection_name=collection_name
        )

        context = retrieval_res["context"]
        citations = retrieval_res["citations"]
        results = retrieval_res["results"]

        if not context or len(results) == 0:
            return QueryResponse(
                question=question,
                answer="⚠️ **Insufficient Evidence in HLD**: No relevant architectural evidence found in the indexed documents for this query. Please check if the component or interface is mentioned in this document version.",
                citations=[],
                confidence=0.0,
                limitation_indicator="No matching context chunks retrieved from vector store.",
                is_inferred=False,
                evidence_found=False
            )

        # Build prompt
        system_prompt = AUTOSAR_RAG_SYSTEM_PROMPT.format(context=context)
        answer_text = llm_service.generate_chat_response(
            system_prompt=system_prompt,
            user_prompt=question
        )

        # Calculate average confidence based on retrieval similarity scores
        avg_score = sum(r.get("score", 0.8) for r in results) / len(results)
        confidence = round(min(0.98, max(0.65, avg_score)), 2)

        # Detect if answer expresses inference
        is_inferred = any(w in answer_text.lower() for w in ["inferred", "likely", "assumed", "suggests", "probable"])
        limitation_indicator = "Answer is strictly grounded in retrieved HLD document sections."
        if is_inferred:
            limitation_indicator = "Contains architectural inference; requires verification against AUTOSAR Software Architecture Model."

        # Audit log
        doc_name = results[0].get("document_name", "All Documents") if results else "Unknown"
        crud.create_audit_log(
            db=db,
            user=user,
            action="RAG Engineering Q&A",
            document=doc_name,
            result=f"Answered with {len(citations)} citations (Confidence: {int(confidence*100)}%)",
            details=f"Query: {question}"
        )

        return QueryResponse(
            question=question,
            answer=answer_text,
            citations=citations,
            confidence=confidence,
            limitation_indicator=limitation_indicator,
            is_inferred=is_inferred,
            evidence_found=True
        )


rag_service = RAGService()
