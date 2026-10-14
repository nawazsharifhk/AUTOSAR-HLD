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
from frontend.components.ui_components import render_hero_banner, get_asil_badge

st.set_page_config(page_title="Architecture Analysis | AutoHLD-AI", page_icon="🔍", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Architecture Analysis & Entity Extraction",
    subtitle="Decomposed AUTOSAR Software Components (SWCs), Sender-Receiver / Client-Server Interfaces, Ports, and Signal Payloads"
)

# Select document
docs = []
try:
    r = requests.get(f"{API_URL}/api/documents", timeout=5)
    if r.status_code == 200:
        docs = r.json()
except Exception:
    pass

if not docs:
    st.warning("⚠️ No documents indexed. Please upload an HLD PDF in the 'Document Upload' page first.")
    st.stop()

doc_options = {f"{d['name']} (v{d['version']})": d["id"] for d in docs}
selected_doc_label = st.selectbox("Select HLD Document to Analyze:", list(doc_options.keys()))
selected_doc_id = doc_options[selected_doc_label]

# Fetch architecture data
try:
    res = requests.get(f"{API_URL}/api/analysis/document/{selected_doc_id}", timeout=10)
    if res.status_code == 200:
        arch_data = res.json()
        components = arch_data.get("components", [])
        interfaces = arch_data.get("interfaces", [])
        dependencies = arch_data.get("dependencies", [])
        findings = arch_data.get("findings", [])
    else:
        st.error("Failed to load architecture data.")
        st.stop()
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
    st.stop()

# Tabs for Views
tab1, tab2, tab3, tab4 = st.tabs([
    "🧩 Software Components (SWCs)",
    "🔌 Interfaces & Signals",
    "🔗 Dependency Matrix",
    "📋 Raw Architecture JSON"
])

with tab1:
    st.markdown(f"### Extracted Components ({len(components)})")
    
    # Filter by ASIL
    asils = list(set(c.get("asil_level", "ASIL-B") for c in components))
    selected_asils = st.multiselect("Filter by Safety Level (ASIL):", asils, default=asils)
    
    filtered_comps = [c for c in components if c.get("asil_level", "ASIL-B") in selected_asils]
    
    for comp in filtered_comps:
        with st.container():
            st.markdown(f"""
            <div class="fluent-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 18px; font-weight: 700; color: #1e293b;">
                        📦 {comp['name']} <span style="font-size: 13px; font-weight: 400; color: #64748b;">({comp['type']})</span>
                    </div>
                    <div>
                        {get_asil_badge(comp.get('asil_level', 'ASIL-B'))}
                        <span style="font-size: 12px; color: #64748b; margin-left: 8px;">Page {comp.get('page', 1)}</span>
                    </div>
                </div>
                <div style="font-size: 14px; color: #374151; margin-bottom: 12px;">{comp.get('description', '')}</div>
                <div style="display: flex; gap: 24px; font-size: 13px; color: #64748b;">
                    <div><b style="color: #1e293b;">Required Ports (R-Ports):</b> <code>{', '.join(comp.get('ports_in', [])) or 'None'}</code></div>
                    <div><b style="color: #1e293b;">Provided Ports (P-Ports):</b> <code>{', '.join(comp.get('ports_out', [])) or 'None'}</code></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown(f"### Extracted Interfaces & Signal Flows ({len(interfaces)})")
    if interfaces:
        iface_rows = []
        for i in interfaces:
            iface_rows.append({
                "Interface Name": i["name"],
                "Source SWC": i["source"],
                "Target SWC": i["target"],
                "Type": i["interface_type"],
                "Signals": ", ".join(i.get("signals", [])),
                "Page": i.get("page", 1)
            })
        st.dataframe(pd.DataFrame(iface_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No interfaces extracted.")

with tab3:
    st.markdown("### 🔗 Component Dependency Matrix")
    if dependencies:
        dep_rows = []
        for d in dependencies:
            dep_rows.append({
                "Caller / Source": d["from_component"],
                "Callee / Target": d["to_component"],
                "Interface Name": d["interface"],
                "Coupling Type": d["type"]
            })
        st.dataframe(pd.DataFrame(dep_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No dependencies extracted.")

with tab4:
    st.json(arch_data)
