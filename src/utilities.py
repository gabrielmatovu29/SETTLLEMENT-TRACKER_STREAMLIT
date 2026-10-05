import streamlit as st

def apply_style():
    st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    .nav-wrap {
        background: #f5f7fa;
        border-radius: 10px;
        padding: 8px 10px;
        margin-bottom: 18px;
        border: 1px solid #e2e6ea;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e2e6ea;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def top_nav():
    st.markdown("""
    <style>
    .top-nav {
        background: #172B4D;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .top-nav-title {
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    div[data-testid="stPageLink-NavLink"] a {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="top-nav">
        <div class="top-nav-title">
             SETTLEMENT TRACKER
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(7)
    links = [
        ("Home", "pages/1_Dashboard.py"),
        ("Uploads", "pages/2_Uploads.py"),
        ("Combined Statement", "pages/3_Big_Statement.py"),
        ("Citi", "pages/4_Citi_Statement.py"),
        ("BOU", "pages/5_BOU_Statement.py"),
        ("Cash Flow", "pages/6_Cash_Flow.py"),
        ("Identifiers", "pages/7_Identifiers.py"),
    ]
    for col, (label, path) in zip(cols, links):
        with col:
            st.page_link(
                path,
                label=label,
                use_container_width=True
            )

def money_range(x):
    try:
        x = abs(float(x))
    except Exception:
        return ""
    if x < 500_000:
        return "<500k"
    elif x < 1_000_000:
        return "500K-1M"
    elif x < 2_000_000:
        return "1M-2M"
    return ">2M"

def read_excel(uploaded_file):
    return __import__("pandas").read_excel(uploaded_file)
