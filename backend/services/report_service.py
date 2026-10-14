import os
import json
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.database import crud
from backend.models.schemas import ExportRequest


class ReportService:
    def __init__(self, reports_dir: str = "./data/reports"):
        self.reports_dir = reports_dir
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)

    def generate_report(self, db: Session, request: ExportRequest) -> Dict[str, Any]:
        """
        Generate structured architecture report in specified format (PDF, DOCX, Excel, JSON).
        """
        doc = crud.get_document_by_id(db, request.document_id)
        if not doc:
            raise ValueError(f"Document with ID {request.document_id} not found.")

        components = crud.get_components_by_document(db, doc.id)
        interfaces = crud.get_interfaces_by_document(db, doc.id)
        findings = crud.get_findings_by_document(db, doc.id)

        fmt = request.format.lower()
        filename = f"AutoHLD_Report_{doc.name.replace('.pdf', '')}_{doc.version}.{fmt}"
        file_path = os.path.join(self.reports_dir, filename)

        if fmt == "json":
            self._generate_json(file_path, doc, components, interfaces, findings)
        elif fmt in ("xlsx", "excel"):
            filename = f"AutoHLD_Report_{doc.name.replace('.pdf', '')}_{doc.version}.xlsx"
            file_path = os.path.join(self.reports_dir, filename)
            self._generate_excel(file_path, doc, components, interfaces, findings)
        elif fmt in ("docx", "doc"):
            filename = f"AutoHLD_Report_{doc.name.replace('.pdf', '')}_{doc.version}.docx"
            file_path = os.path.join(self.reports_dir, filename)
            self._generate_docx(file_path, doc, components, interfaces, findings)
        else:
            # Default to PDF
            filename = f"AutoHLD_Report_{doc.name.replace('.pdf', '')}_{doc.version}.pdf"
            file_path = os.path.join(self.reports_dir, filename)
            self._generate_pdf(file_path, doc, components, interfaces, findings)

        crud.create_audit_log(
            db=db,
            user="Automotive Lead",
            action="Report Export",
            document=doc.name,
            result=f"Generated {fmt.upper()} report",
            details=f"File: {filename}"
        )

        return {
            "filename": filename,
            "file_path": file_path,
            "format": fmt,
            "document_name": doc.name,
            "components_count": len(components),
            "interfaces_count": len(interfaces),
            "findings_count": len(findings)
        }

    def _generate_json(self, path: str, doc, components, interfaces, findings):
        data = {
            "project": "AutoHLD-AI Architecture Report",
            "document": {
                "name": doc.name,
                "version": doc.version,
                "project_id": doc.project_id,
                "upload_date": str(doc.upload_date),
                "page_count": doc.page_count
            },
            "components": [
                {
                    "name": c.name,
                    "type": c.type,
                    "description": c.description,
                    "page": c.page,
                    "asil_level": c.asil_level,
                    "ports_in": c.ports_in,
                    "ports_out": c.ports_out
                } for c in components
            ],
            "interfaces": [
                {
                    "name": i.name,
                    "source": i.source,
                    "target": i.target,
                    "interface_type": i.interface_type,
                    "signals": i.signals,
                    "page": i.page
                } for i in interfaces
            ],
            "findings": [
                {
                    "type": f.type,
                    "description": f.description,
                    "evidence": f.evidence,
                    "confidence": f.confidence,
                    "status": f.status,
                    "reviewer": f.reviewer,
                    "review_notes": f.review_notes
                } for f in findings
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _generate_excel(self, path: str, doc, components, interfaces, findings):
        import pandas as pd
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Overview Sheet
            overview_df = pd.DataFrame([{
                "Document Name": doc.name,
                "Version": doc.version,
                "Project ID": doc.project_id,
                "Page Count": doc.page_count,
                "Components Count": len(components),
                "Interfaces Count": len(interfaces),
                "Findings Count": len(findings),
                "Export Date": str(doc.upload_date)
            }])
            overview_df.to_excel(writer, sheet_name="Overview", index=False)

            # Components Sheet
            comp_rows = [{
                "Name": c.name,
                "Type": c.type,
                "ASIL Level": c.asil_level,
                "Page": c.page,
                "Description": c.description,
                "Ports In": ", ".join(c.ports_in or []),
                "Ports Out": ", ".join(c.ports_out or [])
            } for c in components]
            pd.DataFrame(comp_rows).to_excel(writer, sheet_name="Components", index=False)

            # Interfaces Sheet
            iface_rows = [{
                "Interface Name": i.name,
                "Source Component": i.source,
                "Target Component": i.target,
                "Type": i.interface_type,
                "Signals": ", ".join(i.signals or []),
                "Page": i.page
            } for i in interfaces]
            pd.DataFrame(iface_rows).to_excel(writer, sheet_name="Interfaces", index=False)

            # Findings Sheet
            finding_rows = [{
                "Type": f.type,
                "Description": f.description,
                "Evidence": f.evidence,
                "Confidence": f.confidence,
                "Review Status": f.status,
                "Reviewer": f.reviewer,
                "Review Notes": f.review_notes
            } for f in findings]
            pd.DataFrame(finding_rows).to_excel(writer, sheet_name="Findings & Review", index=False)

    def _generate_docx(self, path: str, doc, components, interfaces, findings):
        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            d = Document()
            d.add_heading(f"AutoHLD-AI Architecture Report: {doc.name}", level=0)
            d.add_paragraph(f"Version: {doc.version} | Project: {doc.project_id} | Pages: {doc.page_count}")

            d.add_heading("1. Extracted Software Components (SWCs)", level=1)
            for c in components:
                p = d.add_paragraph()
                p.add_run(f"• {c.name} ({c.type}) - [{c.asil_level}] (Page {c.page})\n").bold = True
                p.add_run(f"  Description: {c.description}\n")

            d.add_heading("2. Architectural Interfaces", level=1)
            for i in interfaces:
                p = d.add_paragraph()
                p.add_run(f"• {i.name}: {i.source} ➔ {i.target}\n").bold = True
                p.add_run(f"  Type: {i.interface_type} | Signals: {', '.join(i.signals or [])}\n")

            d.add_heading("3. Architecture Findings & Review Status", level=1)
            for f in findings:
                p = d.add_paragraph()
                p.add_run(f"• [{f.status}] {f.type} (Confidence: {int(f.confidence*100)}%)\n").bold = True
                p.add_run(f"  Issue: {f.description}\n")
                p.add_run(f"  Evidence: {f.evidence}\n")
                p.add_run(f"  Reviewer: {f.reviewer} | Notes: {f.review_notes}\n")

            d.save(path)
        except Exception as e:
            print(f"DOCX generation note: {e}")
            self._generate_json(path.replace(".docx", ".json"), doc, components, interfaces, findings)

    def _generate_pdf(self, path: str, doc, components, interfaces, findings):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc_pdf = SimpleDocTemplate(path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#0f172a")
            )
            elements.append(Paragraph(f"AutoHLD-AI Architecture Report", title_style))
            elements.append(Paragraph(f"<b>Document:</b> {doc.name} (v{doc.version}) | <b>Project:</b> {doc.project_id}", styles['Normal']))
            elements.append(Spacer(1, 15))

            # Section 1: Components
            elements.append(Paragraph("<b>1. Extracted Software Components (SWCs)</b>", styles['Heading2']))
            comp_table_data = [["Component Name", "Type", "ASIL", "Page"]]
            for c in components[:12]:
                comp_table_data.append([c.name, c.type, c.asil_level or "ASIL-B", str(c.page)])
            
            comp_table = Table(comp_table_data, colWidths=[180, 160, 80, 50])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ]))
            elements.append(comp_table)
            elements.append(Spacer(1, 15))

            # Section 2: Interfaces
            elements.append(Paragraph("<b>2. Extracted Interfaces & Signal Flows</b>", styles['Heading2']))
            iface_table_data = [["Interface", "Source Component", "Target Component", "Type"]]
            for i in interfaces[:12]:
                iface_table_data.append([i.name, i.source, i.target, i.interface_type])

            iface_table = Table(iface_table_data, colWidths=[160, 140, 140, 90])
            iface_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284c7")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ]))
            elements.append(iface_table)
            elements.append(Spacer(1, 15))

            # Section 3: Findings
            elements.append(Paragraph("<b>3. Architecture Inconsistencies & Human Review</b>", styles['Heading2']))
            for f in findings:
                p_f = Paragraph(f"• <b>[{f.status}]</b> <i>{f.type}</i>: {f.description} (Evidence: {f.evidence})", styles['Normal'])
                elements.append(p_f)
                elements.append(Spacer(1, 4))

            doc_pdf.build(elements)
        except Exception as e:
            print(f"PDF generation note: {e}")
            self._generate_json(path.replace(".pdf", ".json"), doc, components, interfaces, findings)


report_service = ReportService()
