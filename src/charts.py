import pandas as pd
import streamlit as st

def show_comparison(results):
    if not results:
        st.warning("No results to display")
        return

    df = pd.DataFrame(results)

    st.subheader("Execution Time Comparison")
    st.bar_chart(df.set_index("algorithm")["time"])

    st.subheader("Cost Comparison")
    st.bar_chart(df.set_index("algorithm")["cost"])