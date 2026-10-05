import streamlit as st
from src.utilities import apply_style, top_nav
from src.processing import (
    process_cashflow, process_citi_identifiers, process_bou_identifiers,
    process_citi, process_bou, build_big_statement
)

apply_style()
top_nav()
st.title(" Upload Files")

# st.write("Upload the five Excel inputs used by the settlement tracker.")

citi_file = st.file_uploader(
    "1. Citibank Statement",
    type=["xlsx", "xls"],
    key="upload_citi"
)

bou_file = st.file_uploader(
    "2. BOU Statement",
    type=["xlsx", "xls"],
    key="upload_bou"
)

cashflow_file = st.file_uploader(
    "3. Cash Flow",
    type=["xlsx", "xls"],
    key="upload_cashflow"
)

citi_ids_file = st.file_uploader(
    "4. Citi Identifiers",
    type=["xlsx", "xls"],
    key="upload_citi_ids"
)

bou_ids_file = st.file_uploader(
    "5. BOU Identifiers",
    type=["xlsx", "xls"],
    key="upload_bou_ids"
)

if st.button(" Process Files", type="primary", use_container_width=True):
    missing = []
    for name, f in [
        ("Citibank Statement", citi_file),
        ("BOU Statement", bou_file),
        ("Cash Flow", cashflow_file),
        ("Citi Identifiers", citi_ids_file),
        ("BOU Identifiers", bou_ids_file),
    ]:
        if f is None:
            missing.append(name)

    if missing:
        st.error("Missing: " + ", ".join(missing))
        st.stop()

    try:
        with st.spinner("Processing settlement files..."):
            citi_ids = process_citi_identifiers(citi_ids_file)
            bou_ids = process_bou_identifiers(bou_ids_file)
            cashflow = process_cashflow(cashflow_file)
            citi = process_citi(citi_file, citi_ids)
            bou = process_bou(bou_file, bou_ids)
            big = build_big_statement(cashflow, citi, bou)

            st.session_state.citi_ids = citi_ids
            st.session_state.bou_ids = bou_ids
            st.session_state.cashflow = cashflow
            st.session_state.citi = citi
            st.session_state.bou = bou
            st.session_state.big_statement = big
            st.session_state.processed = True

        st.success("All files processed successfully.")
        st.write(f"Cash Flow: **{len(cashflow):,}** rows")
        st.write(f"Citi Statement: **{len(citi):,}** rows")
        st.write(f"BOU Statement: **{len(bou):,}** rows")
        st.write(f"Final settlement output: **{len(big):,}** rows")
    except Exception as e:
        st.error(f"Processing failed: {e}")
