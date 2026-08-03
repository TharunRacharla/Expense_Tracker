import streamlit as st
import pandas as pd
from datetime import datetime
from db_models.database import get_connection
from logic.accounts import update_balance


def load_accounts():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, name, account_type, current_balance FROM accounts ORDER BY id",
        conn,
    )
    conn.close()
    return df


def load_transactions():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            t.id,
            t.txn_date,
            a1.name AS account,
            COALESCE(a2.name, '-') AS destination,
            t.txn_type,
            t.category,
            t.description,
            t.amount
        FROM transactions t
        JOIN accounts a1 ON t.account_id=a1.id
        LEFT JOIN accounts a2 ON t.destination_account_id=a2.id
        ORDER BY t.txn_date DESC
        """,
        conn,
    )
    conn.close()
    return df


def insert_transaction(record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (
            account_id,
            destination_account_id,
            txn_date,
            txn_type,
            category,
            description,
            amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["account_id"],
            record.get("destination_account_id"),
            record["txn_date"],
            record["txn_type"],
            record.get("category"),
            record.get("description"),
            record["amount"],
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def format_currency(amount):
    return f"₹{amount:,.2f}"


st.title("Transactions")
st.write("Manage incomes, expenses, and transfers with account visibility at the top.")

accounts_df = load_accounts()

st.subheader("Account Details")
if accounts_df.empty:
    st.warning("No accounts are available. Create accounts first in the CLI or database.")
else:
    st.dataframe(accounts_df, use_container_width=True)

st.markdown("---")

transactions_df = load_transactions()
if transactions_df.empty:
    st.info("No transactions recorded yet.")
else:
    st.subheader("Recent Transactions")
    st.dataframe(transactions_df, use_container_width=True)

st.markdown("---")

st.subheader("Add or Manage Transactions")
with st.form("transaction_form"):
    txn_type = st.selectbox("Transaction Type", ["income", "expense", "transfer"])

    if accounts_df.empty:
        st.info("Add accounts before creating transactions.")
    else:
        account_options = accounts_df.set_index("id")["name"].to_dict()
        account_id = st.selectbox("Account", list(account_options.keys()), format_func=lambda x: f"{x} - {account_options[x]}")

        destination_account_id = None
        if txn_type == "transfer":
            destination_account_id = st.selectbox(
                "Destination Account",
                [aid for aid in account_options.keys() if aid != account_id],
                format_func=lambda x: f"{x} - {account_options[x]}",
            )

        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.text_input("Category")
        description = st.text_input("Description")
        txn_date = st.date_input("Transaction Date", datetime.today().date())
        txn_time = st.time_input("Transaction Time", datetime.now().time().replace(second=0, microsecond=0))

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            full_date = datetime.combine(txn_date, txn_time)
            insert_transaction(
                {
                    "account_id": account_id,
                    "destination_account_id": destination_account_id,
                    "txn_date": full_date,
                    "txn_type": txn_type,
                    "category": category,
                    "description": description,
                    "amount": amount,
                }
            )

            if txn_type == "income":
                update_balance(account_id, amount, "+")
            elif txn_type == "expense":
                update_balance(account_id, amount, "-")
            else:
                update_balance(account_id, amount, "-")
                update_balance(destination_account_id, amount, "+")

            st.success("Transaction saved successfully.")
            st.rerun()

st.markdown("---")

st.subheader("Transaction Totals")
if not transactions_df.empty:
    totals = transactions_df.groupby("txn_type")["amount"].sum().reset_index()
    st.dataframe(totals, use_container_width=True)
    st.bar_chart(totals.set_index("txn_type")
                 ["amount"])
