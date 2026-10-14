FLUENT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary-glow: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%);
    --accent-blue: #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-cyan: #06b6d4;
    --card-bg: rgba(255, 255, 255, 0.85);
    --card-border: rgba(226, 232, 240, 0.8);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    letter-spacing: -0.01em;
}

/* ── App Background ─────────────────────────────────────── */
.stApp {
    background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.05), transparent 40%),
                radial-gradient(circle at bottom left, rgba(6, 182, 212, 0.05), transparent 40%),
                #f8fafc;
    min-height: 100vh;
}

/* ── Sidebar Styling ─────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f19 0%, #111827 50%, #0f172a 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25);
}
section[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
section[data-testid="stSidebar"] .stCaption * {
    color: #94a3b8 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Sidebar navigation links enhancement */
section[data-testid="stSidebar"] ul li div {
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] ul li div:hover {
    background: rgba(99, 102, 241, 0.18) !important;
}

/* ── Glassmorphic Cards ──────────────────────────────────── */
.fluent-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
}
.fluent-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 12px 30px -4px rgba(99, 102, 241, 0.12), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
}
.fluent-card b, .fluent-card strong {
    color: #0f172a;
    font-weight: 700;
}

/* ── Metric Cards with High Contrast & Gradient Borders ─── */
.metric-container {
    display: flex;
    align-items: center;
    gap: 16px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05);
    transition: all 0.25s ease;
    backdrop-filter: blur(12px);
    position: relative;
    height: 110px;
    box-sizing: border-box;
}
.metric-container::before {
    content: '';
    position: absolute;
    left: 0;
    top: 16px;
    bottom: 16px;
    width: 4px;
    border-radius: 0 4px 4px 0;
    background: linear-gradient(180deg, #4f46e5 0%, #06b6d4 100%);
}
.metric-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px -4px rgba(79, 70, 229, 0.15);
    border-color: rgba(99, 102, 241, 0.4);
}
.metric-icon {
    font-size: 26px;
    min-width: 46px;
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border-radius: 12px;
    flex-shrink: 0;
}
.metric-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
    width: 100%;
}
.metric-label {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.metric-value {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    font-family: 'Plus Jakarta Sans', sans-serif;
    letter-spacing: -0.02em;
}
.metric-delta {
    font-size: 11.5px;
    color: #059669;
    font-weight: 700;
    margin-top: 2px;
    white-space: nowrap;
}

/* ── Hero Banner ─────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 75%, #0284c7 100%);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #ffffff !important;
    padding: 30px 36px;
    border-radius: 18px;
    margin-bottom: 26px;
    box-shadow: 0 16px 40px -10px rgba(67, 56, 202, 0.35);
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-title {
    font-size: 28px !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    margin: 0 !important;
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}
.hero-subtitle {
    font-size: 14.5px !important;
    color: rgba(241, 245, 249, 0.92) !important;
    margin-top: 8px !important;
    margin-bottom: 0 !important;
    line-height: 1.6 !important;
    max-width: 850px;
}

/* ── Badges & Chips ──────────────────────────────────────── */
.badge-asil-d {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.25) 100%);
    color: #b91c1c;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    box-shadow: 0 1px 3px rgba(220, 38, 38, 0.1);
}
.badge-asil-c {
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(234, 88, 12, 0.25) 100%);
    color: #c2410c;
    border: 1px solid rgba(249, 115, 22, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.badge-asil-b {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.25) 100%);
    color: #b45309;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.badge-qm {
    background: rgba(100, 116, 139, 0.12);
    color: #475569;
    border: 1px solid rgba(100, 116, 139, 0.3);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
}

.chip-review {
    background: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.chip-accepted {
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.chip-rejected {
    background: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

/* ── Citations ───────────────────────────────────────────── */
.citation-box {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
    border: 1px solid rgba(203, 213, 225, 0.8);
    border-left: 4px solid #4f46e5;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 12px;
    font-size: 13.5px;
    color: #1e293b;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}
.citation-box b {
    color: #0f172a;
}
.citation-box blockquote {
    margin: 8px 0 0 0;
    padding-left: 12px;
    border-left: 2px solid #818cf8;
    color: #475569;
    font-style: italic;
}

/* ── Modern Premium Buttons ─────────────────────────────── */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 60%, #4338ca 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #4338ca 0%, #4f46e5 60%, #3730a3 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.45) !important;
}

/* ── Headings ────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {
    color: #0f172a !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* ── Tabs Styling ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(226, 232, 240, 0.5) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #475569 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #4f46e5 !important;
    font-weight: 800 !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08) !important;
}

/* ── Dataframes & Tables ─────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03) !important;
}

/* ── Code Blocks ─────────────────────────────────────────── */
code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    background: rgba(79, 70, 229, 0.07) !important;
    color: #4338ca !important;
    padding: 2px 6px !important;
    border-radius: 5px !important;
    border: 1px solid rgba(79, 70, 229, 0.15) !important;
}
</style>
"""

def apply_fluent_styles():
    import streamlit as st
    st.markdown(FLUENT_CSS, unsafe_allow_html=True)
