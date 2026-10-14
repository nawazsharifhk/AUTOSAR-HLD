import pytest
from backend.services.extraction_service import extraction_service


def test_rule_based_extraction():
    sample_pages = [
        {
            "page_number": 1,
            "text": "BrakeController Component (ASIL-D). Controls braking logic.\nVehicleController Component (ASIL-D).\nBrakeController -> VehicleController via BrakeCommandInterface.",
            "section": "1.0 Overview"
        }
    ]

    res = extraction_service.extract_architecture(
        document_id=999,
        full_text=sample_pages[0]["text"],
        pages_data=sample_pages
    )

    comps = [c.name for c in res["components"]]
    assert "BrakeController" in comps or "VehicleController" in comps
    assert len(res["interfaces"]) >= 1
