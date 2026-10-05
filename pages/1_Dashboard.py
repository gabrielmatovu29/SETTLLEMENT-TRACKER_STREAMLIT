import streamlit as st
from src.utilities import apply_style, top_nav

apply_style()
top_nav()

st.title("Home")

if not st.session_state.get("processed"):
    st.warning("Please upload and process the files first.")
    st.stop()

df = st.session_state.big_statement.copy()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("Filters")

st.sidebar.markdown("### Payment Status")

statuses = sorted(
    df["GEN STATUS"]
    .dropna()
    .astype(str)
    .unique()
)

selected_status = st.sidebar.multiselect(
    "Select status",
    statuses,
    default=statuses,
    label_visibility="collapsed"
)

st.sidebar.markdown("### Currency")

currencies = sorted(
    df["Currency"]
    .dropna()
    .astype(str)
    .unique()
)

selected_currency = st.sidebar.multiselect(
    "Select currency",
    currencies,
    default=currencies,
    label_visibility="collapsed"
)

if st.sidebar.button(
    "🔄 Reset Filters",
    use_container_width=True
):
    st.rerun()

# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()

if selected_status:
    filtered = filtered[
        filtered["GEN STATUS"]
        .astype(str)
        .isin(selected_status)
    ]

if selected_currency:
    filtered = filtered[
        filtered["Currency"]
        .astype(str)
        .isin(selected_currency)
    ]

# =========================================================
# DASHBOARD HEADER
# =========================================================

st.markdown(
    "### Settlement Overview"
)

# =========================================================
# KPI CARDS
# =========================================================

total = len(filtered)

paid = filtered[
    filtered["GEN STATUS"]
    .astype(str)
    .str.contains("Paid", case=False, na=False)
].shape[0]

received = filtered[
    filtered["GEN STATUS"]
    .astype(str)
    .str.contains("Received", case=False, na=False)
].shape[0]

outstanding = filtered[
    filtered["GEN STATUS"]
    .astype(str)
    .str.contains(
        "Not Paid|Not Received",
        case=False,
        regex=True,
        na=False
    )
].shape[0]

internal = filtered[
    filtered["GEN STATUS"]
    .astype(str)
    .str.upper()
    .eq("INTERNAL")
].shape[0]

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Transactions",
    f"{total:,}"
)

c2.metric(
    "Paid",
    f"{paid:,}"
)

c3.metric(
    "Received",
    f"{received:,}"
)

c4.metric(
    "Outstanding",
    f"{outstanding:,}"
)

c5.metric(
    "Internal",
    f"{internal:,}"
)

st.divider()

# =========================================================
# FILTERED SETTLEMENT OUTPUT
# =========================================================

st.markdown("### Settlement Transactions")

st.caption(
    f"Showing {len(filtered):,} transaction(s)"
)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
    height=600
)