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

st.set_page_config(page_title="Ask HLD | AutoHLD-AI", page_icon="💬", layout="wide")
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="Ask HLD — Conversational RAG Architecture Assistant",
    subtitle="Ask natural language questions about AUTOSAR components, ports, interfaces, and safety allocations with strict page citations"
)

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your AUTOSAR Architecture Assistant. Ask me anything about components, interfaces, ASIL safety goals, or signals documented in your HLDs.",
            "citations": [],
            "confidence": 1.0,
            "limitation": None
        }
    ]

# Document selector & filters
docs = []
try:
    r = requests.get(f"{API_URL}/api/documents", timeout=5)
    if r.status_code == 200:
        docs = r.json()
except Exception:
    pass

c_sel, c_topk = st.columns([3, 1])
with c_sel:
    doc_options = {"All Documents": None}
    for d in docs:
        doc_options[f"{d['name']} (v{d['version']})"] = d["id"]
    selected_label = st.selectbox("Search Target:", list(doc_options.keys()))
    selected_doc_id = doc_options[selected_label]

with c_topk:
    top_k = st.slider("Top Evidentiary Chunks (k):", min_value=2, max_value=8, value=4)

# Sample Query Chips
st.markdown("**Suggested Engineering Inquiries:**")
quick_queries = [
    "What components depend on BrakeController?",
    "Which interfaces are assigned ASIL-D safety requirements?",
    "Explain the communication flow from RadarInterface to SensorFusion.",
    "What are the periodic execution rates for the runnable entities?"
]

col_q = st.columns(len(quick_queries))
clicked_query = None
for idx, q_text in enumerate(quick_queries):
    with col_q[idx]:
        if st.button(q_text, key=f"q_{idx}", use_container_width=True):
            clicked_query = q_text

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display citations if available
        if msg.get("citations"):
            with st.expander(f"📑 Grounded Evidence & Citations ({len(msg['citations'])} sources)"):
                for idx, c in enumerate(msg["citations"], 1):
                    st.markdown(f"""
                    <div class="citation-box">
                        <b>Citation {idx}:</b> Page <b>{c.get('page')}</b> | Section: <i>{c.get('section', 'N/A')}</i><br/>
                        <blockquote>"{c.get('excerpt')}"</blockquote>
                    </div>
                    """, unsafe_allow_html=True)

        if msg.get("confidence") is not None and msg["role"] == "assistant" and len(msg.get("citations", [])) > 0:
            conf_pct = int(msg["confidence"] * 100)
            st.caption(f"🎯 Retrieval Confidence: **{conf_pct}%** | {msg.get('limitation') or 'Strictly grounded in HLD context'}")

# Handle user input
user_input = st.chat_input("Ask an architectural question about your AUTOSAR HLD...") or clicked_query

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call RAG API
    with st.chat_message("assistant"):
        with st.spinner("Searching vector index & synthesizing grounded architecture answer..."):
            payload = {
                "question": user_input,
                "document_id": selected_doc_id,
                "project_id": "ADAS-Chassis-2026",
                "top_k": top_k
            }
            try:
                res = requests.post(f"{API_URL}/api/query", json=payload, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "")
                    citations = data.get("citations", [])
                    conf = data.get("confidence", 0.85)
                    limitation = data.get("limitation_indicator")

                    st.markdown(answer)

                    if citations:
                        with st.expander(f"📑 Grounded Evidence & Citations ({len(citations)} sources)"):
                            for idx, c in enumerate(citations, 1):
                                st.markdown(f"""
                                <div class="citation-box">
                                    <b>Citation {idx}:</b> Page <b>{c.get('page')}</b> | Section: <i>{c.get('section', 'N/A')}</i><br/>
                                    <blockquote>"{c.get('excerpt')}"</blockquote>
                                </div>
                                """, unsafe_allow_html=True)

                    st.caption(f"🎯 Retrieval Confidence: **{int(conf*100)}%** | {limitation}")

                    # Save to state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations,
                        "confidence": conf,
                        "limitation": limitation
                    })
                else:
                    st.error(f"Query error: {res.text}")
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")
