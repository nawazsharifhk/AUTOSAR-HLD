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
from frontend.components.graph_view import render_plotly_architecture_graph

st.set_page_config(page_title="Architecture Graph | AutoHLD-AI", page_icon="🕸️", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Architecture Relationship Topology Graph",
    subtitle="Interactive NetworkX & Plotly visualization mapping Software Components, Interfaces, and Safety Levels"
)

# Document selection
docs = []
try:
    r = requests.get(f"{API_URL}/api/documents", timeout=5)
    if r.status_code == 200:
        docs = r.json()
except Exception:
    pass

if not docs:
    st.warning("⚠️ No documents available. Please upload an HLD PDF first.")
    st.stop()

doc_options = {f"{d['name']} (v{d['version']})": d["id"] for d in docs}
selected_label = st.selectbox("Select Target Document:", list(doc_options.keys()))
selected_doc_id = doc_options[selected_label]

# Fetch graph data
try:
    res = requests.get(f"{API_URL}/api/analysis/document/{selected_doc_id}/graph", timeout=10)
    if res.status_code == 200:
        graph_data = res.json()
    else:
        st.error("Failed to load graph data.")
        st.stop()
except Exception as e:
    st.error(f"Error connecting to backend: {e}")
    st.stop()

# Graph Metrics Summary
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total SWC Nodes", graph_data.get("node_count", 0))
with c2:
    st.metric("Interface Edges", graph_data.get("edge_count", 0))
with c3:
    cycles = graph_data.get("cycles", [])
    st.metric("Cyclic Dependencies", len(cycles), delta="Clean" if len(cycles) == 0 else "Warning", delta_color="inverse")
with c4:
    orphans = graph_data.get("orphans", [])
    st.metric("Isolated SWCs", len(orphans))

# Legend
st.markdown("""
<div style="display: flex; gap: 14px; margin: 12px 0; font-size: 12px; align-items: center; color: #94a3b8;">
    <b style="color: #f8fafc;">Safety Legend:</b>
    <span class="badge-asil-d">ASIL-D (Critical)</span>
    <span class="badge-asil-c">ASIL-C</span>
    <span class="badge-asil-b">ASIL-B</span>
    <span class="badge-qm">QM (Quality Management)</span>
</div>
""", unsafe_allow_html=True)

# Render Plotly Graph
fig = render_plotly_architecture_graph(graph_data, height=600)
st.plotly_chart(fig, use_container_width=True)

# Graph Analytics Details
with st.expander("🔍 Detailed Network Topology & Degree Centrality"):
    in_deg = graph_data.get("in_degree", {})
    out_deg = graph_data.get("out_degree", {})
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("##### In-Degree (Inbound Receivers)")
        for k, v in in_deg.items():
            st.write(f"• **{k}**: {v} incoming interfaces")
    with col_b:
        st.write("##### Out-Degree (Outbound Senders)")
        for k, v in out_deg.items():
            st.write(f"• **{k}**: {v} outgoing interfaces")
