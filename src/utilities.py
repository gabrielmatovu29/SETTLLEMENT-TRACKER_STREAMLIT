import pandas as pd
import streamlit as st


def apply_style():
    """Apply global CSS styles for padding and UI cards."""
    st.markdown(
        """      """,
        unsafe_allow_html=True,
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