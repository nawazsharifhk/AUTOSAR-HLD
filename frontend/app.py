import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import requests
import pandas as pd
from frontend.styles import apply_fluent_styles
from frontend.components.ui_components import render_hero_banner, render_metric_card, get_asil_badge, get_status_chip

st.set_page_config(
    page_title="AutoHLD-AI | Engineering Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"


def fetch_api(endpoint: str):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/car-service.png", width=64)
    st.markdown("### **AutoHLD-AI**")
    st.caption("GenAI-Powered AUTOSAR HLD Document Analysis & Traceability Assistant")
    st.divider()

    st.markdown("**Workspace Context**")
    project_id = st.selectbox("Active Project", ["ADAS-Chassis-2026", "Powertrain-BMS-2026", "Body-Gateway-2026"])
    
    st.markdown("**Engine Status**")
    health = fetch_api("/api/health")
    if health and health.get("status") == "healthy":
        st.success("● Backend REST API Online")
    else:
        st.warning("○ Backend Connecting (Local Fallback Ready)")

    st.divider()
    st.caption("AutoHLD-AI v1.0.0 • DeepMind Automotive AI")


# Main Dashboard
render_hero_banner(
    title="AutoHLD-AI Architecture Dashboard",
    subtitle="Evidence-grounded engineering intelligence platform for AUTOSAR High-Level Design specifications"
)

# Quick stats row
docs = fetch_api("/api/documents") or []
findings = fetch_api("/api/analysis/findings") or []

total_docs = len(docs)
total_pages = sum(d.get("page_count", 0) for d in docs)
pending_findings = len([
    f for f in findings
    if "Review" in f.get("status", "")
])
accepted_findings = len([
    f for f in findings
    if "Accepted" in f.get("status", "")
])

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Active HLD Documents", str(total_docs), "📄", delta="Live")
with col2:
    render_metric_card("Total Parsed Pages", str(total_pages), "📑")
with col3:
    render_metric_card("Pending AI Findings", str(pending_findings), "⚠️")
with col4:
    render_metric_card("Reviewed & Approved", str(accepted_findings), "✅")

st.markdown("<br>", unsafe_allow_html=True)

# Overview Columns
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.markdown("### 📚 Indexed HLD Documents")
    if docs:
        doc_table_data = []
        for d in docs:
            doc_table_data.append({
                "ID": d["id"],
                "Document Name": d["name"],
                "Version": f"v{d['version']}",
                "Project": d["project_id"],
                "Pages": d["page_count"],
                "Status": d["status"]
            })
        st.dataframe(pd.DataFrame(doc_table_data), use_container_width=True, hide_index=True)
    else:
        st.info("No documents indexed yet. Head to **Document Upload** in the sidebar to index your first HLD PDF!")

    st.markdown("### ⚡ Quick Navigation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.switch_page("pages/1_📄_Document_Upload.py")
    with c2:
        if st.button("💬 Ask Architecture", use_container_width=True):
            st.switch_page("pages/3_💬_Ask_HLD.py")
    with c3:
        if st.button("🔄 Compare Diff", use_container_width=True):
            st.switch_page("pages/5_🔄_Compare_Revisions.py")
    with c4:
        if st.button("🤖 ML Analytics", use_container_width=True):
            st.switch_page("pages/8_🤖_ML_Analytics.py")

with right_col:
    pending_items = [f for f in findings if "Review" in f.get("status", "")]
    st.markdown(f"### 🚨 High-Priority AI Findings ({len(pending_items)} Pending)")
    if pending_items:
        for f in pending_items[:4]:
            with st.container():
                st.markdown(f"""
                <div class="fluent-card" style="padding: 14px 18px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <b style="color: #1e293b;">{f['type']}</b>
                        {get_status_chip(f['status'])}
                    </div>
                    <div style="font-size: 13px; color: #374151; margin-bottom: 6px;">{f['description']}</div>
                    <div style="font-size: 11px; color: #64748b;">Confidence: <b style="color: #4f46e5;">{int(f.get('confidence', 0.85)*100)}%</b> | {f.get('evidence', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        if st.button(f"Review All {len(pending_items)} Findings ➔", width="stretch"):
            st.switch_page("pages/6_✅_Findings_&_Review.py")
    else:
        st.success("All detected architecture findings have been reviewed and resolved.")

st.divider()

# System Architecture & Flow Map
st.markdown("### 🗺️ AutoHLD-AI End-to-End Pipeline")
st.markdown("""
```mermaid
graph LR
    A[📄 AUTOSAR HLD PDF] --> B[⚙️ Ingestion & Parsing]
    B --> C[✂️ Context-Aware Chunking]
    C --> D[🧬 BGE / E5 Embeddings]
    D --> E[(📦 ChromaDB Vector Store)]
    C --> F[(🗄️ SQLite Structured DB)]
    
    Q[🙋 Engineer Architecture Question] --> R[🔍 RAG Semantic Retriever]
    E --> R
    R --> S[🤖 Azure OpenAI / GenAI LLM]
    S --> T[📑 Grounded Answer + Citations]
    
    T --> U[👨‍💻 Human-in-the-Loop Review]
    U --> V[📊 Structured Audit & Reports]
```
""")
