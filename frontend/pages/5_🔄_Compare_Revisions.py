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
from frontend.components.ui_components import render_hero_banner, render_metric_card, get_asil_badge

st.set_page_config(page_title="Compare Revisions | AutoHLD-AI", page_icon="🔄", layout="wide")

# Apply modern aesthetic UI styles
apply_fluent_styles()

API_URL = "http://127.0.0.1:8000"

render_hero_banner(
    title="HLD Revision Comparison Engine",
    subtitle="Detect architectural delta between two HLD releases: +Added, -Removed, ~Modified components & breaking interface changes",
    badge_text="ISO 26262 Diff Analyzer"
)

# Fetch available documents
docs = []
try:
    r = requests.get(f"{API_URL}/api/documents", timeout=5)
    if r.status_code == 200:
        docs = r.json()
except Exception:
    pass

if len(docs) < 2:
    st.info("💡 You need at least two documents indexed to run a revision comparison. You can load sample v1.0 and v2.0 in 'Document Upload'.")
    st.stop()

# Group unique documents by display label with ID to prevent duplicates
doc_map = {f"#{d['id']} - {d['name']} (v{d['version']}) [Uploaded: {d.get('uploaded_by', 'User')}]": d["id"] for d in docs}
labels = list(doc_map.keys())

# Baseline and target selectors
col1, col2 = st.columns(2)
with col1:
    v1_label = st.selectbox("📌 Baseline Document (v1):", labels, index=0, key="select_v1")
    v1_id = doc_map[v1_label]
with col2:
    default_idx = 1 if len(labels) > 1 else 0
    v2_label = st.selectbox("🚀 Updated Revision (v2):", labels, index=default_idx, key="select_v2")
    v2_id = doc_map[v2_label]

current_pair_key = f"{v1_id}_vs_{v2_id}"

# Clear cached diff if the user changes selections
if st.session_state.get("last_compared_pair") != current_pair_key and "diff_result" in st.session_state:
    del st.session_state["diff_result"]

if v1_id == v2_id:
    st.warning("⚠️ Please select two different document versions to compare.")

col_btn, _ = st.columns([1, 2])
with col_btn:
    run_comparison = st.button("⚡ Run Architectural Revision Comparison", width="stretch")

if run_comparison:
    if v1_id == v2_id:
        st.error("Cannot compare a document against itself. Please select two distinct documents.")
    else:
        with st.spinner("Analyzing architectural delta, port modifications, and functional safety impacts..."):
            try:
                res = requests.post(
                    f"{API_URL}/api/compare",
                    json={"doc_v1_id": v1_id, "doc_v2_id": v2_id},
                    timeout=30
                )
                if res.status_code == 200:
                    st.session_state["diff_result"] = res.json()
                    st.session_state["last_compared_pair"] = current_pair_key
                    st.session_state["comparison_pair_name"] = f"{v1_label} ➔ {v2_label}"
                else:
                    st.error(f"Comparison failed: {res.text}")
            except Exception as e:
                st.error(f"Connection error to backend: {e}")

if "diff_result" in st.session_state and st.session_state.get("last_compared_pair") == current_pair_key:
    diff = st.session_state["diff_result"]
    pair_name = st.session_state.get("comparison_pair_name", "")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Executive Summary Card
    st.markdown(f"""
    <div class="fluent-card" style="border-left: 4px solid #4f46e5; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #0f172a; font-weight: 800;">Executive Comparison Summary</h4>
            <span style="font-size: 11px; background: rgba(79, 70, 229, 0.1); color: #4338ca; padding: 3px 10px; border-radius: 20px; font-weight: 700;">
                {pair_name}
            </span>
        </div>
        <div style="font-size: 14.5px; color: #334155; line-height: 1.6;">{diff['summary']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate exact counts
    added_comps = diff.get("added_components", [])
    added_ifaces = diff.get("added_interfaces", [])
    removed_comps = diff.get("removed_components", [])
    removed_ifaces = diff.get("removed_interfaces", [])
    mod_comps = diff.get("modified_components", [])
    mod_ifaces = diff.get("modified_interfaces", [])
    inconsistencies = diff.get("inconsistencies", [])
    
    total_added = len(added_comps) + len(added_ifaces)
    total_removed = len(removed_comps) + len(removed_ifaces)
    total_modified = len(mod_comps) + len(mod_ifaces)
    total_risks = len(inconsistencies)

    # 4 Cards directly matching the 4 tabs below
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Added Entities", f"+{total_added}", "➕", delta=f"{len(added_comps)} SWCs, {len(added_ifaces)} Ifcs")
    with m2:
        render_metric_card("Removed Entities", f"-{total_removed}", "➖", delta=f"{len(removed_comps)} SWCs, {len(removed_ifaces)} Ifcs" if total_removed else "None")
    with m3:
        render_metric_card("Modified Entities", f"~{total_modified}", "🔄", delta=f"{len(mod_comps)} SWCs, {len(mod_ifaces)} Ifcs" if total_modified else "None")
    with m4:
        render_metric_card("Breaking Risks", f"!{total_risks}", "⚠️", delta="Needs Review" if total_risks else "Clean")

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Tabs with identical numbers as the cards
    tab_add, tab_rem, tab_mod, tab_inc = st.tabs([
        f"➕ Added Entities (+{total_added})",
        f"➖ Removed Entities (-{total_removed})",
        f"🔄 Modified Entities (~{total_modified})",
        f"🚨 Breaking Changes & Inconsistencies (!{total_risks})"
    ])

    with tab_add:
        st.markdown(f"### Added Entities: {total_added} total (+{len(added_comps)} Components, +{len(added_ifaces)} Interfaces)")
        c_a1, c_a2 = st.columns([1.2, 1])
        with c_a1:
            st.markdown(f"#### 📦 Added Software Components ({len(added_comps)})")
            if added_comps:
                for comp in added_comps:
                    asil_badge = get_asil_badge(comp.get("asil_level", "ASIL-B"))
                    st.markdown(f"""
                    <div class="fluent-card" style="border-left: 4px solid #10b981; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <b style="color: #0f172a; font-size: 15px;">{comp['name']}</b>
                            {asil_badge}
                        </div>
                        <div style="font-size: 12.5px; color: #64748b; margin-bottom: 6px;">Type: <b>{comp.get('type', 'SWC')}</b> | Defined Page: {comp.get('page', 1)}</div>
                        <div style="font-size: 13.5px; color: #334155;">{comp.get('description', '')}</div>
                        <div style="margin-top: 8px; font-size: 12px; color: #475569;">
                            <b>Ports:</b> In: <code>{', '.join(comp.get('ports_in', []))}</code> | Out: <code>{', '.join(comp.get('ports_out', []))}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No newly added components identified between these revisions.")

        with c_a2:
            st.markdown(f"#### 🔗 Added Interfaces ({len(added_ifaces)})")
            if added_ifaces:
                st.dataframe(pd.DataFrame(added_ifaces), width="stretch", hide_index=True)
            else:
                st.info("No newly added interfaces identified.")

    with tab_rem:
        st.markdown(f"### Removed Entities: {total_removed} total (-{len(removed_comps)} Components, -{len(removed_ifaces)} Interfaces)")
        c_r1, c_r2 = st.columns([1.2, 1])
        with c_r1:
            st.markdown(f"#### 🗑️ Removed Components ({len(removed_comps)})")
            if removed_comps:
                for comp in removed_comps:
                    st.markdown(f"""
                    <div class="fluent-card" style="border-left: 4px solid #ef4444; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <b style="color: #991b1b; font-size: 15px;">{comp['name']}</b>
                            <span style="background: rgba(239, 68, 68, 0.1); color: #dc2626; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">REMOVED</span>
                        </div>
                        <div style="font-size: 12.5px; color: #64748b; margin-bottom: 6px;">Type: {comp.get('type', 'SWC')} | Previous Page: {comp.get('page', 1)}</div>
                        <div style="font-size: 13.5px; color: #334155;">{comp.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No components were removed in this revision.")

        with c_r2:
            st.markdown(f"#### 🔌 Removed Interfaces ({len(removed_ifaces)})")
            if removed_ifaces:
                st.dataframe(pd.DataFrame(removed_ifaces), width="stretch", hide_index=True)
            else:
                st.success("No existing interfaces were deprecated.")

    with tab_mod:
        st.markdown(f"### Modified Entities: {total_modified} total (~{len(mod_comps)} Components, ~{len(mod_ifaces)} Interfaces)")
        c_m1, c_m2 = st.columns([1.2, 1])
        with c_m1:
            st.markdown(f"#### 🔄 Modified Components ({len(mod_comps)})")
            if mod_comps:
                for mod in mod_comps:
                    st.markdown(f"""
                    <div class="fluent-card" style="border-left: 4px solid #f59e0b; padding: 16px;">
                        <b style="color: #0f172a; font-size: 15px;">{mod['name']}</b>
                        <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #334155; font-size: 13.5px;">
                            {''.join([f"<li>{c}</li>" for c in mod.get('changes', [])])}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No modifications detected in existing components.")

        with c_m2:
            st.markdown(f"#### 📡 Modified Interfaces ({len(mod_ifaces)})")
            if mod_ifaces:
                st.dataframe(pd.DataFrame(mod_ifaces), width="stretch", hide_index=True)
            else:
                st.info("No modifications detected in interfaces.")

    with tab_inc:
        st.markdown(f"### Detected Inconsistencies & Risks: {total_risks} total")
        if inconsistencies:
            for inc in inconsistencies:
                sev = inc.get("severity", "High")
                sev_color = "#dc2626" if sev == "High" else "#ea580c"
                st.markdown(f"""
                <div class="fluent-card" style="border-left: 4px solid {sev_color}; padding: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <b style="color: {sev_color}; font-size: 15px;">{inc['type']}</b>
                        <span style="background: {sev_color}18; color: {sev_color}; border: 1px solid {sev_color}40; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 12px;">
                            Severity: {sev}
                        </span>
                    </div>
                    <div style="font-size: 14px; color: #1e293b; margin-bottom: 8px; line-height: 1.5;">{inc['description']}</div>
                    <div style="font-size: 13px; color: #4338ca; background: rgba(79, 70, 229, 0.06); padding: 8px 12px; border-radius: 6px;">
                        <b>Recommended Action:</b> {inc.get('action', 'Manual architect signoff')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Zero architectural inconsistencies or breaking changes detected between these revisions!")
