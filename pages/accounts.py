from datetime import datetime

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
        "SELECT id, name, account_type, opening_balance, starting_balance_update_time, current_balance, credit_limit FROM accounts ORDER BY id",
        conn,
    )
    conn.close()
    balances = load_account_transaction_delta()
    df = df.merge(balances, on="id", how="left")
    df["transaction_delta"] = df["transaction_delta"].fillna(0)
    df["computed_balance"] = df["opening_balance"] + df["transaction_delta"]
    df["current_balance"] = df["computed_balance"]
    if not df["current_balance"].equals(df["current_balance"]):
        pass
    reconcile_account_balances(df[["id", "computed_balance"]])
    return df


def load_account_transaction_delta():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            a.id,
            COALESCE(SUM(
                CASE
                    WHEN t.txn_type = 'income' AND t.account_id = a.id THEN t.amount
                    WHEN t.txn_type = 'expense' AND t.account_id = a.id THEN -t.amount
                    WHEN t.txn_type = 'transfer' AND t.account_id = a.id THEN -t.amount
                    WHEN t.txn_type = 'transfer' AND t.destination_account_id = a.id THEN t.amount
                    ELSE 0
                END
            ), 0) AS transaction_delta
        FROM accounts a
        LEFT JOIN transactions t ON (t.account_id = a.id OR t.destination_account_id = a.id)
            AND (a.starting_balance_update_time IS NULL OR t.txn_date >= a.starting_balance_update_time)
        GROUP BY a.id
        """,
        conn,
    )
    conn.close()
    return df


def reconcile_account_balances(balances_df):
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in balances_df.iterrows():
        cursor.execute(
            "UPDATE accounts SET current_balance = ? WHERE id = ?",
            (row["computed_balance"], row["id"]),
        )
    conn.commit()
    cursor.close()
    conn.close()


def insert_account(name, account_type, opening_balance, starting_balance_update_time, credit_limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO accounts (
            name,
            account_type,
            opening_balance,
            starting_balance_update_time,
            current_balance,
            credit_limit
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, account_type, opening_balance, starting_balance_update_time, opening_balance, credit_limit),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_account(account_id, name, account_type, current_balance, credit_limit, starting_balance_update_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE accounts
        SET name = ?,
            account_type = ?,
            current_balance = ?,
            credit_limit = ?,
            starting_balance_update_time = ?
        WHERE id = ?
        """,
        (name, account_type, current_balance, credit_limit, starting_balance_update_time, account_id),
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
        starting_balance_date = st.date_input("Starting Balance Effective Date", value=datetime.today().date())
        starting_balance_time = st.time_input("Starting Balance Effective Time", value=datetime.now().time().replace(second=0, microsecond=0))
        starting_balance_update_time = datetime.combine(starting_balance_date, starting_balance_time)
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
                insert_account(name, account_type, opening_balance, starting_balance_update_time, credit_limit)
                st.success("Account created successfully.")
                st.rerun()

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

    def parse_datetime(value):
        if isinstance(value, datetime):
            return value
        if value is None:
            return datetime.now().replace(second=0, microsecond=0)
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except Exception:
                continue
        return datetime.now().replace(second=0, microsecond=0)

    selected_start_time = parse_datetime(selected["starting_balance_update_time"])

    with st.form("edit_account_form"):
        edit_name = st.text_input("Name", value=selected["name"])
        edit_type = st.selectbox("Account Type", ACCOUNT_TYPES, index=ACCOUNT_TYPES.index(selected["account_type"]))
        edit_current_balance = st.number_input("Current Balance", value=float(selected["current_balance"]), format="%.2f")
        edit_starting_balance_date = st.date_input("Starting Balance Effective Date", value=selected_start_time.date())
        edit_starting_balance_time = st.time_input("Starting Balance Effective Time", value=selected_start_time.time().replace(second=0, microsecond=0))
        edit_starting_balance_update_time = datetime.combine(edit_starting_balance_date, edit_starting_balance_time)
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
                update_account(selected_id, edit_name, edit_type, edit_current_balance, edit_credit_limit, edit_starting_balance_update_time)
                st.success("Account updated successfully.")
                st.rerun()

    if st.button("Delete account", key="delete_account_button"):
        delete_account(selected_id)
        st.warning("Account deleted.")
        st.rerun()
