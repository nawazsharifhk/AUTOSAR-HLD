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
from frontend.components.ui_components import render_hero_banner, get_status_chip

st.set_page_config(page_title="Findings & Review | AutoHLD-AI", page_icon="✅", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Human-in-the-Loop Architecture Review",
    subtitle="Engineers remain in control: review, accept, reject, or edit AI-detected findings with strict governance and audit logging"
)

# Fetch findings
findings = []
try:
    res = requests.get(f"{API_URL}/api/analysis/findings", timeout=10)
    if res.status_code == 200:
        findings = res.json()
except Exception as e:
    st.error(f"Error connecting to backend: {e}")

if not findings:
    st.info("No architectural findings detected or awaiting review.")
    st.stop()

# Filter by Status
status_filter = st.selectbox(
    "Filter by Review Status:",
    ["All Findings", "Requires Engineer Review", "Accepted", "Rejected", "Edited"]
)

filtered = findings
if status_filter != "All Findings":
    filtered = [f for f in findings if f.get("status") == status_filter]

st.markdown(f"### Active Findings for Review ({len(filtered)})")

for f in filtered:
    fid = f["id"]
    with st.container():
        st.markdown(f"""
        <div class="fluent-card" style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-size: 16px; font-weight: 700; color: #1e293b;">
                    ⚠️ Finding #{fid}: {f['type']}
                </div>
                <div>{get_status_chip(f['status'])}</div>
            </div>
            <div style="font-size: 14px; color: #374151; margin-bottom: 10px;">
                <b style="color: #1e293b;">Description:</b> {f['description']}
            </div>
            <div style="background: rgba(239,246,255,0.9); border: 1px solid rgba(99,102,241,0.2); border-radius: 6px; padding: 8px 12px; font-size: 13px; margin-bottom: 12px; color: #374151;">
                <b style="color: #4f46e5;">Evidence Grounding:</b> <i>"{f.get('evidence', 'Extracted from document')}"</i>
            </div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">
                Confidence Score: <b style="color: #4f46e5;">{int(f.get('confidence', 0.85)*100)}%</b> | Reviewer: <b style="color: #1e293b;">{f.get('reviewer', 'Pending')}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"⚙️ Take Action on Finding #{fid}"):
            col_act, col_notes = st.columns([1, 2])
            with col_act:
                action = st.radio(
                    "Select Decision:",
                    ["Accept Finding", "Reject Finding", "Edit Finding"],
                    key=f"rad_{fid}"
                )
                reviewer_name = st.text_input("Reviewer Sign-off Name", value="Lead Safety Engineer", key=f"rev_{fid}")
            
            with col_notes:
                notes = st.text_area("Architect / Engineering Rationale:", value=f.get("review_notes", ""), key=f"notes_{fid}")
                if st.button("💾 Submit Review Decision", key=f"sub_{fid}", use_container_width=True):
                    status_map = {
                        "Accept Finding": "Accepted",
                        "Reject Finding": "Rejected",
                        "Edit Finding": "Edited"
                    }
                    payload = {
                        "status": status_map[action],
                        "reviewer": reviewer_name,
                        "review_notes": notes
                    }
                    try:
                        up_res = requests.put(f"{API_URL}/api/analysis/findings/{fid}", json=payload)
                        if up_res.status_code == 200:
                            st.success(f"Finding #{fid} recorded as '{status_map[action]}'.")
                            st.rerun()
                        else:
                            st.error(f"Update failed: {up_res.text}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")
