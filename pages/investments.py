import streamlit as st
import pandas as pd
from datetime import date
from db_models.database import get_connection


def load_accounts():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, name FROM accounts WHERE account_type='dmat' ORDER BY name",
        conn,
    )
    conn.close()
    return df


def load_holdings():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            h.id,
            a.name AS account,
            h.asset_name,
            h.asset_type,
            h.amount_invested,
            h.last_updated_value,
            h.investment_type,
            h.sip_amount,
            h.sip_frequency,
            h.start_date,
            h.notes,
            h.updated_on
        FROM holdings h
        JOIN accounts a ON h.account_id=a.id
        ORDER BY h.asset_name
        """,
        conn,
    )
    conn.close()
    return df


def insert_holding(record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO holdings (
            account_id,
            asset_name,
            asset_type,
            amount_invested,
            last_updated_value,
            investment_type,
            sip_amount,
            sip_frequency,
            start_date,
            notes,
            updated_on
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["account_id"],
            record["asset_name"],
            record["asset_type"],
            record["amount_invested"],
            record["last_updated_value"],
            record["investment_type"],
            record.get("sip_amount"),
            record.get("sip_frequency"),
            record.get("start_date"),
            record.get("notes"),
            record.get("updated_on"),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_holding_value(holding_id, new_value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE holdings SET last_updated_value=?, updated_on=? WHERE id=?",
        (new_value, date.today().isoformat(), holding_id),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_holding(holding_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM holdings WHERE id=?", (holding_id,))
    conn.commit()
    cursor.close()
    conn.close()


def format_currency(value):
    return f"₹{value:,.2f}"


st.title("Investments")
st.write("Manage DMAT investments and keep current values updated.")

holdings_df = load_holdings()
accounts_df = load_accounts()

st.subheader("Current Holdings")
if holdings_df.empty:
    st.info("No investment holdings available.")
else:
    holdings_df["gain_loss"] = holdings_df["last_updated_value"] - holdings_df["amount_invested"]
    st.dataframe(holdings_df, use_container_width=True)
    st.markdown("---")

if accounts_df.empty:
    st.warning("No DMAT accounts found. Add an account of type 'dmat' before adding investments.")
else:
    with st.expander("Add New Investment"):
        account_options = accounts_df.set_index("id")["name"].to_dict()
        account_id = st.selectbox(
            "DMAT Account", list(account_options.keys()), format_func=lambda x: f"{x} - {account_options[x]}"
        )
        asset_name = st.text_input("Asset Name")
        asset_type = st.selectbox(
            "Asset Type",
            ["mutual_fund", "stock", "etf", "gold", "fd", "bond", "other"],
        )
        amount_invested = st.number_input("Amount Invested", min_value=0.0, format="%.2f")
        last_updated_value = st.number_input("Current Value", min_value=0.0, format="%.2f")
        investment_type = st.selectbox("Investment Type", ["one_time", "sip"])
        sip_amount = None
        sip_frequency = None
        start_date = None

        if investment_type == "sip":
            sip_amount = st.number_input("SIP Amount", min_value=0.0, format="%.2f")
            sip_frequency = st.selectbox("SIP Frequency", ["weekly", "monthly", "quarterly", "yearly"])
            start_date = st.date_input("SIP Start Date", date.today()).isoformat()

        notes = st.text_area("Notes")
        updated_on = st.date_input("Updated On", date.today()).isoformat()

        if st.button("Add Investment"):
            if not asset_name:
                st.error("Asset name is required.")
            else:
                insert_holding(
                    {
                        "account_id": account_id,
                        "asset_name": asset_name,
                        "asset_type": asset_type,
                        "amount_invested": amount_invested,
                        "last_updated_value": last_updated_value,
                        "investment_type": investment_type,
                        "sip_amount": sip_amount,
                        "sip_frequency": sip_frequency,
                        "start_date": start_date,
                        "notes": notes,
                        "updated_on": updated_on,
                    }
                )
                st.success("Investment added successfully.")
                st.rerun()

with st.expander("Update or Delete Existing Investment"):
    if holdings_df.empty:
        st.info("No holdings to update or delete.")
    else:
        holding_options = holdings_df.set_index("id")["asset_name"].to_dict()
        selected_id = st.selectbox(
            "Select Holding",
            list(holding_options.keys()),
            format_func=lambda x: f"{x} - {holding_options[x]}",
        )
        new_value = st.number_input("New Current Value", min_value=0.0, format="%.2f")

        if st.button("Update Value"):
            update_holding_value(selected_id, new_value)
            st.success("Holding value updated.")
            st.rerun()

        if st.button("Delete Investment", key="delete_investment"):
            delete_holding(selected_id)
            st.success("Investment deleted.")
            st.rerun()
