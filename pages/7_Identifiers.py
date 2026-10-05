import streamlit as st
from src.utilities import apply_style#, top_nav
from src.processing import (
    process_citi_identifiers, process_bou_identifiers,
    save_citi_identifiers, save_bou_identifiers,
    process_citi, process_bou, build_big_statement
)
st.set_page_config(layout="wide")
apply_style()
#top_nav()

st.subheader("Identifiers")

# Initialize identifiers in session state if not loaded yet
if "citi_ids" not in st.session_state:
    st.session_state.citi_ids = process_citi_identifiers()

if "bou_ids" not in st.session_state:
    st.session_state.bou_ids = process_bou_identifiers()

tab1, tab2 = st.tabs(["Citi Identifiers", "BOU Identifiers"])

with tab1:
    st.caption("Edit Citi Identifiers directly below and save changes.")
    edited_citi_ids = st.data_editor(
        st.session_state.citi_ids,
        num_rows="dynamic",
        use_container_width=True,
        key="citi_editor"
    )
    if st.button("💾 Save Citi Identifiers", key="save_citi"):
        save_citi_identifiers(edited_citi_ids)
        st.session_state.citi_ids = edited_citi_ids
        st.success("Citi Identifiers updated and saved to data/citi_identifiers.xlsx!")

        # Re-run reconciliation if main statements exist in state
        if st.session_state.get("processed") and "raw_citi_file" in st.session_state:
            citi = process_citi(st.session_state.raw_citi_file, edited_citi_ids)
            big = build_big_statement(st.session_state.cashflow, citi, st.session_state.bou)
            st.session_state.citi = citi
            st.session_state.big_statement = big
            st.info("Re-calculated Citi statement and Combined Statement with updated identifiers.")

with tab2:
    st.caption("Edit BOU Identifiers directly below and save changes.")
    edited_bou_ids = st.data_editor(
        st.session_state.bou_ids,
        num_rows="dynamic",
        use_container_width=True,
        key="bou_editor"
    )
    if st.button("💾 Save BOU Identifiers", key="save_bou"):
        save_bou_identifiers(edited_bou_ids)
        st.session_state.bou_ids = edited_bou_ids
        st.success("BOU Identifiers updated and saved to data/bou_identifiers.xlsx!")

        if st.session_state.get("processed") and "raw_bou_file" in st.session_state:
            bou = process_bou(st.session_state.raw_bou_file, edited_bou_ids)
            big = build_big_statement(st.session_state.cashflow, st.session_state.citi, bou)
            st.session_state.bou = bou
            st.session_state.big_statement = big
            st.info("Re-calculated BOU statement and Combined Statement with updated identifiers.")