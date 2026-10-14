import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import requests
import pandas as pd
from frontend.styles import apply_fluent_styles
from frontend.components.ui_components import render_hero_banner

st.set_page_config(page_title="Reports & Audit | AutoHLD-AI", page_icon="📊", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Engineering Reports & Compliance Audit Trail",
    subtitle="Generate structured ISO 26262 / AUTOSAR compliance reports in PDF, DOCX, Excel, and JSON formats"
)

tab_export, tab_audit = st.tabs(["📥 Export Architecture Reports", "🛡️ Governance & Audit Trail"])

with tab_export:
    docs = []
    try:
        r = requests.get(f"{API_URL}/api/documents", timeout=5)
        if r.status_code == 200:
            docs = r.json()
    except Exception:
        pass

    if not docs:
        st.warning("No documents available for export. Please upload an HLD PDF first.")
    else:
        doc_map = {f"{d['name']} (v{d['version']})": d["id"] for d in docs}
        selected_label = st.selectbox("Select Target HLD Document:", list(doc_map.keys()))
        selected_doc_id = doc_map[selected_label]

        col1, col2 = st.columns(2)
        with col1:
            report_format = st.selectbox("Export Format:", ["PDF", "Excel (.xlsx)", "Word (.docx)", "JSON"])
        with col2:
            include_findings = st.checkbox("Include Human Review Findings", value=True)

        fmt_code_map = {
            "PDF": "pdf",
            "Excel (.xlsx)": "xlsx",
            "Word (.docx)": "docx",
            "JSON": "json"
        }

        if st.button("📄 Generate & Download Report", use_container_width=True):
            with st.spinner("Compiling structured engineering report..."):
                payload = {
                    "document_id": selected_doc_id,
                    "format": fmt_code_map[report_format],
                    "include_findings": include_findings
                }
                try:
                    res = requests.post(f"{API_URL}/api/export", json=payload, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Report generated: **{data['filename']}**")
                        
                        # Download button
                        download_url = f"{API_URL}{data['download_url']}"
                        r_file = requests.get(download_url)
                        if r_file.status_code == 200:
                            st.download_button(
                                label=f"⬇️ Download {data['filename']}",
                                data=r_file.content,
                                file_name=data["filename"],
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                    else:
                        st.error(f"Report generation error: {res.text}")
                except Exception as ex:
                    st.error(f"Failed to communicate with export service: {ex}")

with tab_audit:
    st.markdown("### 🛡️ System Audit Trail (ISO 26262 Compliance Log)")
    try:
        r_audit = requests.get(f"{API_URL}/api/audit-logs", timeout=5)
        if r_audit.status_code == 200 and r_audit.json():
            logs = r_audit.json()
            log_rows = []
            for l in logs:
                log_rows.append({
                    "Timestamp": l["timestamp"],
                    "User / Engineer": l["user"],
                    "Action": l["action"],
                    "Target Document": l["document"],
                    "Result": l["result"],
                    "Details": l.get("details", "")
                })
            st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs recorded yet.")
    except Exception as e:
        st.warning("Audit service not reachable.")
