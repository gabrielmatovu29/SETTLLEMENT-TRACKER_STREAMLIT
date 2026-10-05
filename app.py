import streamlit as st
from src.utilities import apply_style#, top_nav

st.set_page_config(
    page_title="Settlement Tracker",
    #page_icon="ST",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_style()
#top_nav()

st.title("Settlement Tracker")
st.subheader("Settlement reconciliation dashboard")

if "processed" not in st.session_state:
    st.session_state.processed = False

if not st.session_state.processed:
    st.info("Start from **Uploads**. Upload the five Excel inputs and click **Process Files**.")
else:
    st.success("Files are loaded and processed. Use the navigation above to review the outputs.")

st.markdown("""
### Workflow
1. Upload **Citibank Statement**, **BOU Statement**, **Cash Flow**, **Citi Identifiers**, and **BOU Identifiers**.
2. Click **Process Files**.
3. Review the **Dashboard** and filter by currency or payment status.
4. Open the individual output pages when you need the detailed records.
""")
