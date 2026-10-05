import streamlit as st
from src.utilities import apply_style, top_nav

apply_style()
top_nav()
#st.title(" Identifiers")

if not st.session_state.get("processed"):
    st.warning("Please process the uploads first.")
    st.stop()

tab1, tab2 = st.tabs(["Citi Identifiers", "BOU Identifiers"])

with tab1:
    st.dataframe(st.session_state.citi_ids, use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(st.session_state.bou_ids, use_container_width=True, hide_index=True)
