import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import requests
from frontend.styles import apply_fluent_styles
from frontend.components.ui_components import render_hero_banner

st.set_page_config(page_title="Document Upload | AutoHLD-AI", page_icon="📄", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Document Ingestion & Indexing",
    subtitle="Upload AUTOSAR High-Level Design (HLD) specifications for automated parsing, chunking, and semantic vector indexing"
)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### 📤 Upload New HLD Specification")
    with st.form("upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Select AUTOSAR HLD Document (PDF, TXT, MD)",
            type=["pdf", "txt", "md"],
            help="Upload your automotive system or software high-level design specification"
        )
        
        c_ver, c_proj = st.columns(2)
        with c_ver:
            version = st.text_input("Document Version", value="1.0", help="e.g. 1.0, 2.0, 2.1-draft")
        with c_proj:
            project_id = st.text_input("Project Workspace ID", value="ADAS-Chassis-2026")

        uploaded_by = st.text_input("Author / Engineer Name", value="Lead Automotive Architect")
        
        submit = st.form_submit_button("🚀 Upload and Analyze Document", use_container_width=True)

        if submit:
            if uploaded_file is None:
                st.error("Please select a file to upload.")
            else:
                with st.spinner("Processing document: extracting pages, tables, SWCs, generating BGE embeddings & indexing..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "version": version,
                        "project_id": project_id,
                        "uploaded_by": uploaded_by
                    }
                    try:
                        res = requests.post(f"{API_URL}/api/documents/upload", files=files, data=data, timeout=60)
                        if res.status_code == 200:
                            result = res.json()
                            st.success(f"🎉 **{uploaded_file.name}** successfully indexed!")
                            st.balloons()
                            
                            st.markdown(f"""
                            <div class="fluent-card">
                                <b>Extraction Summary:</b><br/>
                                • <b>Pages Parsed:</b> {result.get('page_count')}<br/>
                                • <b>Vector Chunks:</b> {result.get('chunk_count')}<br/>
                                • <b>Software Components:</b> {result.get('components_count')}<br/>
                                • <b>Interfaces Detected:</b> {result.get('interfaces_count')}<br/>
                                • <b>AI Review Findings:</b> {result.get('findings_count')}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Upload failed: {res.text}")
                    except Exception as e:
                        st.error(f"Connection error to backend: {e}")

with col2:
    st.markdown("### 🧪 Load Pre-packaged Benchmark HLDs")
    st.caption("Instantly test the platform with realistic AUTOSAR Brake & ADAS specifications:")

    sample_dir = "./data/sample_hld"
    samples = [
        ("AUTOSAR_Brake_and_Vehicle_Control_HLD_v1.0.pdf", "1.0", "Baseline Braking Architecture (ASIL-D / QM)"),
        ("AUTOSAR_Brake_and_Vehicle_Control_HLD_v2.0.pdf", "2.0", "Revised ADAS L2+ Architecture with Camera & Eth")
    ]

    for filename, ver, desc in samples:
        path = os.path.join(sample_dir, filename)
        with st.container():
            st.markdown(f"""
            <div class="fluent-card" style="padding: 16px; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #1e293b;">{filename}</div>
                <div style="font-size: 13px; color: #64748b; margin-bottom: 8px;">{desc}</div>
                <span class="badge-asil-d">v{ver}</span>
            </div>
            """, unsafe_allow_html=True)

            if os.path.exists(path):
                if st.button(f"⚡ Re-index {filename}", key=f"btn_{filename}", use_container_width=True):
                    with st.spinner(f"Indexing {filename}..."):
                        with open(path, "rb") as f:
                            files = {"file": (filename, f.read(), "application/pdf")}
                            data = {"version": ver, "project_id": "ADAS-Chassis-2026", "uploaded_by": "System Benchmark"}
                            res = requests.post(f"{API_URL}/api/documents/upload", files=files, data=data, timeout=60)
                            if res.status_code == 200:
                                st.success(f"Indexed {filename} successfully!")
                            else:
                                st.error(res.text)

st.divider()

# List Existing Documents
st.markdown("### 📋 Active Documents in Workspace")
try:
    r = requests.get(f"{API_URL}/api/documents", timeout=5)
    if r.status_code == 200 and r.json():
        for doc in r.json():
            with st.expander(f"📄 {doc['name']} (v{doc['version']}) - {doc['page_count']} Pages"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**Project Workspace:** {doc['project_id']}")
                    st.write(f"**Uploaded By:** {doc['uploaded_by']}")
                    st.write(f"**Date:** {doc['upload_date']}")
                    st.write(f"**Summary:** {doc.get('summary', 'AUTOSAR High-Level Design')}")
                with col_b:
                    if st.button("🗑️ Delete", key=f"del_{doc['id']}", use_container_width=True):
                        requests.delete(f"{API_URL}/api/documents/{doc['id']}")
                        st.rerun()
    else:
        st.info("No documents currently stored.")
except Exception as e:
    st.warning("Backend service unavailable.")
