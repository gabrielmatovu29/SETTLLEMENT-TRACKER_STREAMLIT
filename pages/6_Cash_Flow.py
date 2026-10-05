import streamlit as st
from src.utilities import apply_style#, top_nav

apply_style()
st.set_page_config(layout="wide")
#top_nav()
st.subheader("💰 Cash Flows")


if not st.session_state.get("processed"):
    st.warning("Please process the uploads first.")
    st.stop()

df = st.session_state.cashflow
#st.metric("Rows", len(df))
st.dataframe(df, 
             #use_container_width=True, 
             hide_index=True)

st.download_button(
    "⬇️ Download Cash Flow CSV",
    df.to_csv(index=False).encode("utf-8"),
    "cash_flow.csv",
    "text/csv"
)
