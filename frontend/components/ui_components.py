import streamlit as st
from typing import Optional


def render_hero_banner(title: str, subtitle: str, badge_text: str = "AUTOSAR Classic R4.4 / Adaptive"):
    st.markdown(f"""
    <div class="hero-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 class="hero-title">🚗 {title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
            </div>
            <span style="background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; color: #ffffff;">
                {badge_text}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, icon: str = "📊", delta: Optional[str] = None):
    delta_html = f'<div class="metric-delta">↑ {delta}</div>' if delta else '<div class="metric-delta" style="opacity: 0;">-</div>'
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-icon">{icon}</div>
        <div class="metric-content">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_asil_badge(asil: str) -> str:
    asil_upper = (asil or "QM").upper()
    if "ASIL-D" in asil_upper:
        return f'<span class="badge-asil-d">ASIL-D</span>'
    elif "ASIL-C" in asil_upper:
        return f'<span class="badge-asil-c">ASIL-C</span>'
    elif "ASIL-B" in asil_upper:
        return f'<span class="badge-asil-b">ASIL-B</span>'
    else:
        return f'<span class="badge-qm">{asil or "QM"}</span>'


def get_status_chip(status: str) -> str:
    status_lower = (status or "").lower()
    if "accepted" in status_lower:
        return f'<span class="chip-accepted">✓ Accepted</span>'
    elif "rejected" in status_lower:
        return f'<span class="chip-rejected">✕ Rejected</span>'
    else:
        return f'<span class="chip-review">⏳ Needs Review</span>'
