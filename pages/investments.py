import streamlit as st
import pandas as pd
import plotly.express as px
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


def load_current_month_investment_expense_by_account():
    conn = get_connection()
    today = date.today()
    df = pd.read_sql_query(
        """
        SELECT
            a.name AS account,
            SUM(t.amount) AS total
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.txn_type = 'expense'
            AND lower(COALESCE(t.category, '')) = 'investments'
            AND strftime('%Y', t.txn_date) = ?
            AND strftime('%m', t.txn_date) = ?
        GROUP BY a.name
        ORDER BY total DESC
        """,
        conn,
        params=(today.strftime('%Y'), today.strftime('%m')),
    )
    conn.close()
    return df


def load_yearly_investment_expense_by_account():
    conn = get_connection()
    today = date.today()
    df = pd.read_sql_query(
        """
        SELECT
            strftime('%Y-%m', t.txn_date) AS month,
            a.name AS account,
            SUM(t.amount) AS total
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE t.txn_type = 'expense'
            AND lower(COALESCE(t.category, '')) = 'investments'
            AND strftime('%Y', t.txn_date) = ?
        GROUP BY month, a.name
        ORDER BY month, a.name
        """,
        conn,
        params=(today.strftime('%Y'),),
    )
    conn.close()
    return df


def load_investment_expense_by_account(period="all"):
    conn = get_connection()
    if period == "month":
        today = date.today()
        df = pd.read_sql_query(
            """
            SELECT
                a.name AS account,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.txn_type = 'expense'
                AND lower(COALESCE(t.category, '')) = 'investments'
                AND strftime('%Y', t.txn_date) = ?
                AND strftime('%m', t.txn_date) = ?
            GROUP BY a.name
            ORDER BY total DESC
            """,
            conn,
            params=(today.strftime('%Y'), today.strftime('%m')),
        )
    else:
        df = pd.read_sql_query(
            """
            SELECT
                a.name AS account,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.txn_type = 'expense'
                AND lower(COALESCE(t.category, '')) = 'investments'
            GROUP BY a.name
            ORDER BY total DESC
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

st.subheader("Current Month Investment Mix")
holdings_by_type = (
    holdings_df.groupby("asset_type", as_index=False)["last_updated_value"].sum()
    .rename(columns={"last_updated_value": "total"})
)
expense_by_account = load_current_month_investment_expense_by_account()

pie_rows = []
for _, row in holdings_by_type.iterrows():
    pie_rows.append(
        {
            "label": row["asset_type"].replace("_", " ").title(),
            "total": row["total"],
            "type": "Holding",
        }
    )

for _, row in expense_by_account.iterrows():
    pie_rows.append(
        {
            "label": f"Expense - {row['account']}",
            "total": row["total"],
            "type": "Expense",
        }
    )

if pie_rows:
    pie_df = pd.DataFrame(pie_rows)
    fig = px.pie(
        pie_df,
        names="label",
        values="total",
        color="type",
        title="Current Month Investment Holdings + Investment Expenses",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No holdings or investment-category expenses available for the current month.")

st.markdown("---")

st.subheader("Yearly Investment Expenses by Account")
yearly_df = load_yearly_investment_expense_by_account()
if yearly_df.empty:
    st.info("No yearly investment expense records found.")
else:
    yearly_df["month"] = pd.to_datetime(yearly_df["month"] + "-01")
    fig = px.line(
        yearly_df,
        x="month",
        y="total",
        color="account",
        markers=True,
        title="Yearly Investment Expense Trend by Account",
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        legend_title="Account",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(yearly_df, use_container_width=True)

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

st.markdown("---")

st.subheader("Investment Expense Breakdown")
period = st.radio("Period", ["This month", "All time"], horizontal=True, key="investment_expense_period")
investment_expense_df = load_investment_expense_by_account("month" if period == "This month" else "all")

if investment_expense_df.empty:
    st.info("No investment-category expenses found for this period.")
else:
    st.dataframe(investment_expense_df, use_container_width=True)
    fig = px.bar(
        investment_expense_df,
        x="account",
        y="total",
        color="account",
        title="Investment Expenses by Account",
    )
    fig.update_layout(yaxis_title="Amount (₹)", xaxis_title="Account", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

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
