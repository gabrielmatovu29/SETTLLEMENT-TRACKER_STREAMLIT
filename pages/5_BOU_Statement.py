import streamlit as st
from src.utilities import apply_style#, top_nav

apply_style()
st.set_page_config(layout="wide")
#top_nav()
#st.title(" Bank of Uganda Statement")
st.subheader("Bank of Uganda Statement")

if not st.session_state.get("processed"):
    st.warning("Please process the uploads first.")
    st.stop()

df = st.session_state.bou
#st.metric("Rows", len(df))
st.dataframe(df, 
             #use_container_width=True,
             hide_index=True)

st.download_button(
    "⬇️ Download BOU CSV",
    df.to_csv(index=False).encode("utf-8"),
    "bou_statement.csv",
    "text/csv"
)
