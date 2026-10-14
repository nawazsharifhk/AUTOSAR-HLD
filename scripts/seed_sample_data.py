import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.session import SessionLocal, init_db
from backend.services.document_service import document_service

SAMPLE_DIR = "./data/sample_hld"


def seed_database():
    init_db()
    db = SessionLocal()

    v1_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v1.0.pdf")
    v2_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v2.0.pdf")
    v3_path = os.path.join(SAMPLE_DIR, "AUTOSAR_Brake_and_Vehicle_Control_HLD_v3.0.pdf")

    if not os.path.exists(v1_path) or not os.path.exists(v2_path) or not os.path.exists(v3_path):
        from scripts.generate_sample_hld import build_hld_v1, build_hld_v2, build_hld_v3
        build_hld_v1(v1_path)
        build_hld_v2(v2_path)
        build_hld_v3(v3_path)

    print("--- Seeding AUTOSAR HLD v1.0 ---")
    res_v1 = document_service.process_and_index_pdf(
        db=db,
        file_path=v1_path,
        filename="AUTOSAR_Brake_and_Vehicle_Control_HLD_v1.0.pdf",
        version="1.0",
        project_id="ADAS-Chassis-2026",
        uploaded_by="Lead Safety Architect"
    )
    print(f"v1.0 Indexed: Doc ID {res_v1['document'].id}, {res_v1['components_count']} SWCs, {res_v1['interfaces_count']} Interfaces.")

    print("--- Seeding AUTOSAR HLD v2.0 ---")
    res_v2 = document_service.process_and_index_pdf(
        db=db,
        file_path=v2_path,
        filename="AUTOSAR_Brake_and_Vehicle_Control_HLD_v2.0.pdf",
        version="2.0",
        project_id="ADAS-Chassis-2026",
        uploaded_by="Lead ADAS Architect"
    )
    print(f"v2.0 Indexed: Doc ID {res_v2['document'].id}, {res_v2['components_count']} SWCs, {res_v2['interfaces_count']} Interfaces.")
    
    print("--- Seeding AUTOSAR HLD v3.0 ---")
    res_v3 = document_service.process_and_index_pdf(
        db=db,
        file_path=v3_path,
        filename="AUTOSAR_Brake_and_Vehicle_Control_HLD_v3.0.pdf",
        version="3.0",
        project_id="ADAS-Chassis-2026",
        uploaded_by="Lead AI/ML Architect"
    )
    print(f"v3.0 Indexed: Doc ID {res_v3['document'].id}, {res_v3['components_count']} SWCs, {res_v3['interfaces_count']} Interfaces.")

    db.close()
    print("Seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
