import streamlit as st
import pandas as pd
from db_models.database import get_connection

ACCOUNT_TYPES = [
    "savings",
    "current",
    "credit_card",
    "cash",
    "wallet",
    "dmat",
]


def load_accounts():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, name, account_type, opening_balance, current_balance, credit_limit FROM accounts ORDER BY id",
        conn,
    )
    conn.close()
    return df


def insert_account(name, account_type, opening_balance, credit_limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO accounts (
            name,
            account_type,
            opening_balance,
            current_balance,
            credit_limit
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (name, account_type, opening_balance, opening_balance, credit_limit),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_account(account_id, name, account_type, current_balance, credit_limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE accounts
        SET name = ?,
            account_type = ?,
            current_balance = ?,
            credit_limit = ?
        WHERE id = ?
        """,
        (name, account_type, current_balance, credit_limit, account_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    cursor.close()
    conn.close()


def format_currency(value):
    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return "-"


st.set_page_config(page_title="Accounts", page_icon="🏦", layout="wide")

st.title("Accounts")
st.write("Add, edit, and delete your accounts from a single page.")

accounts_df = load_accounts()

st.subheader("Account list")
if accounts_df.empty:
    st.info("No accounts found. Add a new account below.")
else:
    display_df = accounts_df.copy()
    display_df["opening_balance"] = display_df["opening_balance"].apply(format_currency)
    display_df["current_balance"] = display_df["current_balance"].apply(format_currency)
    display_df["credit_limit"] = display_df["credit_limit"].apply(lambda x: format_currency(x) if x is not None else "-")
    st.dataframe(display_df, use_container_width=True)

st.markdown("---")

with st.expander("Add new account", expanded=True):
    with st.form("add_account_form"):
        name = st.text_input("Account Name")
        account_type = st.selectbox("Account Type", ACCOUNT_TYPES)
        opening_balance = st.number_input("Opening Balance", value=0.0, format="%.2f")
        credit_limit = None

        if account_type == "credit_card":
            outstanding = st.number_input("Current Outstanding", value=0.0, format="%.2f")
            credit_limit = st.number_input("Credit Limit", value=0.0, format="%.2f")
            opening_balance = -abs(outstanding)
        else:
            credit_limit = st.number_input("Credit Limit (optional)", value=0.0, format="%.2f")
            if credit_limit == 0.0:
                credit_limit = None

        submitted = st.form_submit_button("Create account")
        if submitted:
            if not name:
                st.error("Account name is required.")
            else:
                insert_account(name, account_type, opening_balance, credit_limit)
                st.success("Account created successfully.")
                st.experimental_rerun()

st.markdown("---")

st.subheader("Manage existing account")
if accounts_df.empty:
    st.info("Add an account above before editing or deleting.")
else:
    selected_id = st.selectbox(
        "Select account",
        accounts_df["id"].tolist(),
        format_func=lambda x: f"{x} - {accounts_df.loc[accounts_df['id'] == x, 'name'].iloc[0]}"
    )
    selected = accounts_df[accounts_df["id"] == selected_id].iloc[0]

    with st.form("edit_account_form"):
        edit_name = st.text_input("Name", value=selected["name"])
        edit_type = st.selectbox("Account Type", ACCOUNT_TYPES, index=ACCOUNT_TYPES.index(selected["account_type"]))
        edit_current_balance = st.number_input("Current Balance", value=float(selected["current_balance"]), format="%.2f")
        edit_credit_limit = selected["credit_limit"] if selected["credit_limit"] is not None else 0.0
        if edit_type == "credit_card":
            edit_credit_limit = st.number_input("Credit Limit", value=float(edit_credit_limit), format="%.2f")
        else:
            edit_credit_limit = st.number_input("Credit Limit", value=float(edit_credit_limit), format="%.2f")
            if edit_credit_limit == 0.0:
                edit_credit_limit = None

        updated = st.form_submit_button("Update account")
        if updated:
            if not edit_name:
                st.error("Account name is required.")
            else:
                update_account(selected_id, edit_name, edit_type, edit_current_balance, edit_credit_limit)
                st.success("Account updated successfully.")
                st.experimental_rerun()

    if st.button("Delete account", key="delete_account_button"):
        delete_account(selected_id)
        st.warning("Account deleted.")
        st.experimental_rerun()
