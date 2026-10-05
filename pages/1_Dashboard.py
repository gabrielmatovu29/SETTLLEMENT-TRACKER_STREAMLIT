import streamlit as st
from src.utilities import apply_style# top_nav

apply_style()

st.set_page_config(layout="wide")
#top_nav()
st.subheader("Settlement Tracker")
if not st.session_state.get("processed"):
    st.warning("Please upload and process the files first.")
    st.stop()

df = st.session_state.big_statement.copy()

# =========================================================
# SIDEBAR FILTERS (BUTTON / PILL SELECTION)
# =========================================================

st.sidebar.title("Filters")

st.sidebar.markdown("### Payment Status")
statuses = sorted(df["GEN STATUS"].dropna().astype(str).unique())

# Button-style selection using st.pills
selected_status = st.sidebar.pills(
    "Select status",
    options=statuses,
    default=statuses,
    selection_mode="multi",
    label_visibility="collapsed"
)

st.sidebar.markdown("### Currency")
currencies = sorted(df["Currency"].dropna().astype(str).unique())

selected_currency = st.sidebar.pills(
    "Select currency",
    options=currencies,
    default=currencies,
    selection_mode="multi",
    label_visibility="collapsed"
)

if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.rerun()

# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()

if selected_status:
    filtered = filtered[filtered["GEN STATUS"].astype(str).isin(selected_status)]
else:
    filtered = filtered.iloc[0:0]

if selected_currency and not filtered.empty:
    filtered = filtered[filtered["Currency"].astype(str).isin(selected_currency)]

# =========================================================
# KPI CARDS
# =========================================================

total = len(filtered)
paid = filtered[filtered["GEN STATUS"].astype(str).str.contains("Paid", case=False, na=False)].shape[0]
received = filtered[filtered["GEN STATUS"].astype(str).str.contains("Received", case=False, na=False)].shape[0]
outstanding = filtered[filtered["GEN STATUS"].astype(str).str.contains("Not Paid|Not Received", case=False, regex=True, na=False)].shape[0]
internal = filtered[filtered["GEN STATUS"].astype(str).str.upper().eq("INTERNAL")].shape[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Transactions", f"{total:,}")
c2.metric("Paid", f"{paid:,}")
c3.metric("Received", f"{received:,}")
c4.metric("Outstanding", f"{outstanding:,}")
c5.metric("Internal", f"{internal:,}")

st.divider()

# =========================================================
# FILTERED SETTLEMENT OUTPUT
# =========================================================

st.markdown("### Settlement Transactions")
st.caption(f"Showing {len(filtered):,} transaction(s)")

st.dataframe(
    filtered,
    #use_container_width=True,
    hide_index=True,
    height=600
)