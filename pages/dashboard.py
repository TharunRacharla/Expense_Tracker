import streamlit as st
import pandas as pd
from datetime import date
from db_models.database import get_connection
import plotly.express as px

def load_accounts():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, name, account_type, opening_balance, starting_balance_update_time, current_balance FROM accounts ORDER BY account_type, name",
        conn,
    )
    conn.close()
    balances = load_account_transaction_delta()
    df = df.merge(balances, on="id", how="left")
    df["transaction_delta"] = df["transaction_delta"].fillna(0)
    df["computed_balance"] = df["opening_balance"] + df["transaction_delta"]
    df["current_balance"] = df["computed_balance"]
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


def load_monthly_expense_by_category():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            strftime('%Y-%m', txn_date) AS month,
            category,
            SUM(amount) AS total
        FROM transactions
        WHERE txn_type = 'expense'
        GROUP BY month, category
        ORDER BY month
        """,
        conn,
    )
    conn.close()
    if not df.empty:
        df["month"] = pd.to_datetime(df["month"] + "-01")
    return df


def load_investment_expense_by_account(period="all"):
    conn = get_connection()
    if period == "month":
        today = date.today()
        df = pd.read_sql_query(
            """
            SELECT
                a.name AS account,
                lower(COALESCE(t.category, '')) AS category,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.txn_type = 'expense'
                AND lower(COALESCE(t.category, '')) = 'investment'
                AND strftime('%Y', t.txn_date) = ?
                AND strftime('%m', t.txn_date) = ?
            GROUP BY account, category
            ORDER BY account, total DESC
            """,
            conn,
            params=(today.strftime('%Y'), today.strftime('%m')),
        )
    else:
        df = pd.read_sql_query(
            """
            SELECT
                a.name AS account,
                lower(COALESCE(t.category, '')) AS category,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.txn_type = 'expense'
                AND lower(COALESCE(t.category, '')) = 'investment'
            GROUP BY account, category
            ORDER BY account, total DESC
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

st.subheader("Monthly Expense Breakdown")
monthly_category_df = load_monthly_expense_by_category()
if monthly_category_df.empty:
    st.info("No monthly expense records available.")
else:
    fig = px.bar(
        monthly_category_df,
        x="month",
        y="total",
        color="category",
        title="Monthly Expense Breakdown by Category",
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        barmode="stack",
        legend_title="Category",
    )
    fig.update_xaxes(dtick="M1", tickformat="%b")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(monthly_category_df.sort_values(["month", "category"]), use_container_width=True)

st.markdown("---")

st.subheader("Investment Expenses by Account")
period = st.radio("Period", ["This month", "All time"], horizontal=True, key="investment_expense_period")
investment_expense_df = load_investment_expense_by_account("month" if period == "This month" else "all")

if investment_expense_df.empty:
    st.info("No investment expense data found for this period.")
else:
    st.dataframe(investment_expense_df, use_container_width=True)
    chart_df = investment_expense_df.groupby("account", as_index=False)["total"].sum()
    fig = px.bar(chart_df, x="account", y="total", color="account", title="Investment Expenses by Account")
    fig.update_layout(yaxis_title="Amount (₹)", xaxis_title="Account", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Expense by Category")
period = st.radio("Period", ["This month", "All time"], horizontal=True, key="expense_category_period")
expense_df = load_expense_by_category("month" if period == "This month" else "all")
if expense_df.empty:
    st.info("No expense data found for this period.")
else:
    fig = px.pie(expense_df, names="category", values="total")
    st.plotly_chart(fig)

st.markdown("---")
st.subheader("Track Category Improvement Month by Month")
monthly_category_df = load_monthly_expense_by_category()
if monthly_category_df.empty:
    st.info("No monthly category expense data available.")
else:
    categories = monthly_category_df["category"].sort_values().unique().tolist()
    selected_category = st.radio("Choose expense category", categories, horizontal=True, key="category_trend")
    filtered = monthly_category_df[monthly_category_df["category"] == selected_category].copy()
    if filtered.empty:
        st.warning(f"No data found for category: {selected_category}")
    else:
        filtered = filtered.sort_values("month")
        filtered = filtered.set_index("month")
        filtered = filtered.resample("ME")["total"].sum().fillna(0)
        filtered = filtered.rename_axis("Month").reset_index()
        filtered["Month"] = filtered["Month"].dt.strftime("%Y-%m")
        line_fig = px.line(filtered, x="Month", y="total", title=f"{selected_category} expense trend", markers=True)
        line_fig.update_layout(yaxis_title="Expense (₹)", xaxis_title="Month")
        st.plotly_chart(line_fig, use_container_width=True)
        st.dataframe(filtered, use_container_width=True)
