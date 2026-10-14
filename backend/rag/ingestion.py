import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def extract_pages_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text, tables, and page metadata from PDF file.
    Supports PyMuPDF, pdfplumber, and pypdf fallback.
    """
    pages_data = []

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Method 1: PyMuPDF (Fast and accurate)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                # Detect headings or section titles
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                section_title = detect_section_header(lines)

                pages_data.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "section": section_title,
                    "tables": []
                })
            doc.close()
            if pages_data:
                return pages_data
        except Exception as e:
            print(f"PyMuPDF extraction warning: {e}, falling back...")

    # Method 2: pdfplumber (Extracts tables & structured text)
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    tables = page.extract_tables() or []

                    table_text = ""
                    for table in tables:
                        table_text += "\n" + "\n".join([" | ".join([str(cell or "") for cell in row]) for row in table])

                    full_text = text + ("\n[Extracted Table Data]\n" + table_text if table_text else "")
                    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
                    section_title = detect_section_header(lines)

                    pages_data.append({
                        "page_number": idx + 1,
                        "text": full_text,
                        "section": section_title,
                        "tables": tables
                    })
            if pages_data:
                return pages_data
        except Exception as e:
            print(f"pdfplumber extraction warning: {e}, falling back...")

    # Method 3: pypdf fallback
    if PYPDF_AVAILABLE:
        try:
            reader = PdfReader(pdf_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                section_title = detect_section_header(lines)
                pages_data.append({
                    "page_number": idx + 1,
                    "text": text,
                    "section": section_title,
                    "tables": []
                })
            return pages_data
        except Exception as e:
            print(f"pypdf extraction warning: {e}")

    # Plain text file or fallback parser
    if pdf_path.endswith(".txt") or pdf_path.endswith(".md"):
        with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            pages_data.append({
                "page_number": 1,
                "text": content,
                "section": "Document Body",
                "tables": []
            })
        return pages_data

    raise RuntimeError("No suitable PDF extraction library available (install pymupdf, pdfplumber, or pypdf).")


def detect_section_header(lines: List[str]) -> str:
    """
    Heuristic to extract top heading from page lines (e.g. '1.1 System Architecture', '4. Brake Control').
    """
    for line in lines[:5]:
        if re.match(r"^(\d+(\.\d+)*)\s+[A-Za-z]", line) or line.isupper() and len(line) < 60:
            return line
    if lines:
        return lines[0][:60]
    return "General Section"
