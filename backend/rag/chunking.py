import re
from typing import List, Dict, Any


def chunk_document_pages(pages: List[Dict[str, Any]], chunk_size: int = 600, overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Split document pages into context-aware chunks preserving page numbers, section headers, and component tags.
    """
    chunks = []

    # Known automotive component keywords for tag detection
    comp_patterns = [
        r"\b(BrakeController|VehicleController|SensorFusion|RadarInterface|CameraInterface|PowertrainMgr|SafetyController|CAN_Gateway|DiagnosticManager|BatteryManagementSystem|SteeringController|TransmissionController|ADASCruiseControl)\b",
        r"\b(SWC_[A-Za-z0-9_]+|BSW_[A-Za-z0-9_]+|Rte_[A-Za-z0-9_]+)\b"
    ]

    for page_data in pages:
        page_num = page_data["page_number"]
        section = page_data.get("section", f"Page {page_num}")
        text = page_data["text"]

        # Clean text
        text = re.sub(r'\r\n', '\n', text)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) <= chunk_size:
                current_chunk += "\n\n" + p if current_chunk else p
            else:
                if current_chunk:
                    # Detect components in this chunk
                    detected_comps = set()
                    for pat in comp_patterns:
                        detected_comps.update(re.findall(pat, current_chunk))

                    chunks.append({
                        "page": page_num,
                        "section": section,
                        "component": ", ".join(list(detected_comps)[:3]) if detected_comps else "General",
                        "text": current_chunk.strip()
                    })

                # If single paragraph is larger than chunk_size, split by sentences
                if len(p) > chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    sub_chunk = ""
                    for s in sentences:
                        if len(sub_chunk) + len(s) <= chunk_size:
                            sub_chunk += " " + s if sub_chunk else s
                        else:
                            if sub_chunk:
                                detected_comps = set()
                                for pat in comp_patterns:
                                    detected_comps.update(re.findall(pat, sub_chunk))
                                chunks.append({
                                    "page": page_num,
                                    "section": section,
                                    "component": ", ".join(list(detected_comps)[:3]) if detected_comps else "General",
                                    "text": sub_chunk.strip()
                                })
                            sub_chunk = s
                    current_chunk = sub_chunk
                else:
                    current_chunk = p

        if current_chunk:
            detected_comps = set()
            for pat in comp_patterns:
                detected_comps.update(re.findall(pat, current_chunk))
            chunks.append({
                "page": page_num,
                "section": section,
                "component": ", ".join(list(detected_comps)[:3]) if detected_comps else "General",
                "text": current_chunk.strip()
            })

    return chunks
