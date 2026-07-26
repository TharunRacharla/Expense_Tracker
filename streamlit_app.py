import streamlit as st
from db_models.init_db import initialize_database

initialize_database()

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
)

st.title("Expense Tracker")
st.write("Choose a page from the sidebar to open the dashboard, manage transactions, or manage investments.")
st.sidebar.title("Navigation")
st.sidebar.info("Use the Streamlit page menu to access Dashboard, Transactions, and Investments.")
