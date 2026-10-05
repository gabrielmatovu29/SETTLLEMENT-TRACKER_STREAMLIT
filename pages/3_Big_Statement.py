import streamlit as st
from src.utilities import apply_style#, top_nav

apply_style()
st.set_page_config(layout="wide")
#top_nav() 
#st.title("Combined statement")
st.subheader("Combined statement")

if not st.session_state.get("processed"):
    st.warning("Please process the uploads first.")
    st.stop()

df = st.session_state.big_statement
#st.metric("Rows", len(df))
st.dataframe(df,
             #use_container_width=True, 
             hide_index=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Big Statement CSV", csv, "big_statement.csv", "text/csv")
