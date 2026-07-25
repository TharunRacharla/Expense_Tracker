import streamlit as st
import pandas as pd
from datetime import date
from db_models.database import get_connection


def load_accounts():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, name, account_type, current_balance FROM accounts ORDER BY account_type, name",
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
            h.investment_type
        FROM holdings h
        JOIN accounts a ON h.account_id=a.id
        ORDER BY h.asset_type, h.asset_name
        """,
        conn,
    )
    conn.close()
    return df


def load_monthly_cash_flow():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            strftime('%Y-%m', txn_date) AS month,
            txn_type,
            SUM(amount) AS total
        FROM transactions
        WHERE txn_type IN ('income','expense')
        GROUP BY month, txn_type
        ORDER BY month
        """,
        conn,
    )
    conn.close()
    return df




def load_daily_expenses():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            strftime('%Y-%m-%d', txn_date) AS date,
            SUM(amount) AS total_expense
        FROM transactions
        WHERE txn_type = 'expense'
        GROUP BY date
        ORDER BY date
        """,
        conn,
    )
    conn.close()
    return df


def load_expense_by_category(period="all"):
    conn = get_connection()
    if period == "month":
        today = date.today()
        df = pd.read_sql_query(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE txn_type = 'expense'
                AND strftime('%Y', txn_date) = ?
                AND strftime('%m', txn_date) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            conn,
            params=(today.strftime('%Y'), today.strftime('%m')),
        )
    else:
        df = pd.read_sql_query(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE txn_type = 'expense'
            GROUP BY category
            ORDER BY total DESC
            """,
            conn,
        )
    conn.close()
    return df


def calculate_net_worth(accounts, holdings):
    non_dmat = accounts[accounts["account_type"] != "dmat"]
    assets = non_dmat.loc[non_dmat["account_type"] != "credit_card", "current_balance"].sum()
    liabilities = non_dmat.loc[non_dmat["account_type"] == "credit_card", "current_balance"].abs().sum()
    investments = holdings["last_updated_value"].sum() if not holdings.empty else 0
    net_worth = assets + investments - liabilities
    return assets, liabilities, investments, net_worth


def format_currency(value):
    return f"₹{value:,.2f}"


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("Expense Tracker Dashboard")
st.write("A Power BI–style overview of accounts, investments, cash flow, and expense breakdown.")

accounts_df = load_accounts()
holdings_df = load_holdings()
monthly_flow_df = load_monthly_cash_flow()
daily_expense_df = load_daily_expenses()

assets, liabilities, investments, net_worth = calculate_net_worth(accounts_df, holdings_df)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Accounts", len(accounts_df))
kpi2.metric("Cash & Accounts", format_currency(assets))
k3 = kpi3.metric("Investments", format_currency(investments))
k4 = kpi4.metric("Net Worth", format_currency(net_worth))

st.markdown("---")

st.subheader("Monthly Cash Flow")
if monthly_flow_df.empty:
    st.info("No cash flow transactions found.")
else:
    flow_pivot = monthly_flow_df.pivot(index="month", columns="txn_type", values="total").fillna(0)
    flow_pivot["savings"] = flow_pivot.get("income", 0) - flow_pivot.get("expense", 0)
    st.area_chart(flow_pivot)
    st.dataframe(flow_pivot.reset_index(), use_container_width=True)

st.markdown("---")

st.subheader("Daily Expense Trend")
if daily_expense_df.empty:
    st.info("No expense history available.")
else:
    daily_expense_df["date"] = pd.to_datetime(daily_expense_df["date"])
    daily_expense_df = daily_expense_df.set_index("date")
    st.line_chart(daily_expense_df["total_expense"])

st.markdown("---")

st.subheader("Expense by Category")
period = st.radio("Period", ["This month", "All time"], horizontal=True)
expense_df = load_expense_by_category("month" if period == "This month" else "all")
if expense_df.empty:
    st.info("No expense data found for this period.")
else:
    st.bar_chart(expense_df.set_index("category")["total"])
