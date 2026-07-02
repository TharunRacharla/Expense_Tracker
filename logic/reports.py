from db_models.database import get_connection

def account_summary():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            name,
            account_type,
            current_balance
        FROM accounts
        ORDER BY account_type,name
    """)

    rows = cur.fetchall()

    print("\n========== ACCOUNT SUMMARY ==========\n")

    total_assets = 0
    total_liabilities = 0

    for name, acc_type, balance in rows:

        balance = float(balance)

        print(f"{name:<25} ₹{balance:>12,.2f}")

        if acc_type == "credit_card":
            total_liabilities += abs(balance)
        else:
            total_assets += balance

    print("-"*40)

    print(f"Assets      ₹{total_assets:,.2f}")
    print(f"Liabilities ₹{total_liabilities:,.2f}")

def investment_summary():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            asset_name,
            asset_type,
            amount_invested,
            last_updated_value
        FROM holdings
        ORDER BY asset_type,asset_name
    """)

    rows = cur.fetchall()

    invested = 0
    current = 0

    print("\n========== INVESTMENTS ==========\n")

    for row in rows:

        gain = float(row[3]) - float(row[2])

        invested += float(row[2])
        current += float(row[3])

        print(f"{row[0]:30}")
        print(f"Invested : ₹{float(row[2]):,.2f}")
        print(f"Current  : ₹{float(row[3]):,.2f}")
        print(f"Gain     : ₹{gain:,.2f}")
        print()

    print("-"*40)
    print(f"Total Invested : ₹{invested:,.2f}")
    print(f"Current Value  : ₹{current:,.2f}")
    print(f"Profit         : ₹{current-invested:,.2f}")

    cur.close()
    conn.close()

def net_worth():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            account_type,
            current_balance
        FROM accounts
        WHERE account_type <> 'dmat'
    """)

    accounts = cur.fetchall()

    assets = 0
    liabilities = 0

    for acc in accounts:

        balance = float(acc[1])

        if acc[0] == "credit_card":
            liabilities += abs(balance)
        else:
            assets += balance

    cur.execute("""
        SELECT
        SUM(last_updated_value)
        FROM holdings
    """)

    result = cur.fetchone()

    investments = float(result[0] or 0)

    assets += investments

    print("\n========== NET WORTH ==========\n")

    print(f"Cash & Accounts : ₹{assets-investments:,.2f}")
    print(f"Investments     : ₹{investments:,.2f}")
    print(f"Liabilities     : ₹{liabilities:,.2f}")

    print("-"*40)

    print(f"NET WORTH       : ₹{assets-liabilities:,.2f}")

    cur.close()
    conn.close()

def monthly_summary():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            YEAR(txn_date),

            MONTH(txn_date),

            txn_type,

            SUM(amount)

        FROM transactions

        WHERE txn_type IN ('income','expense')

        GROUP BY
            YEAR(txn_date),
            MONTH(txn_date),
            txn_type

        ORDER BY
            YEAR(txn_date),
            MONTH(txn_date)
    """)

    rows = cur.fetchall()

    print("\n====== MONTHLY CASH FLOW ======\n")

    monthly = {}

    for year, month, ttype, amount in rows:

        key = f"{year}-{month:02}"

        if key not in monthly:
            monthly[key] = {"income":0,"expense":0}

        monthly[key][ttype] = float(amount)

    for month,data in monthly.items():

        savings = data["income"]-data["expense"]

        print(f"{month}")
        print(f"Income  : ₹{data['income']:,.2f}")
        print(f"Expense : ₹{data['expense']:,.2f}")
        print(f"Savings : ₹{savings:,.2f}")
        print()

def expense_by_category():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            category,
            SUM(amount)

        FROM transactions

        WHERE txn_type='expense'

        GROUP BY category

        ORDER BY SUM(amount) DESC
    """)

    rows = cur.fetchall()

    print("\n====== EXPENSES BY CATEGORY ======\n")

    for cat,total in rows:

        print(f"{cat:<20} ₹{float(total):>12,.2f}")

    cur.close()
    conn.close()

def run_reports():
    while True:
        print("""========== REPORTS ==========
                1. Account Summary
                2. Investment Summary
                3. Net Worth
                4. Monthly Cash Flow
                5. Expense by Category
                6. Back
              """)
        choice = input("Select action: ")

        if choice == "1":
            account_summary()
        elif choice == "2":
            investment_summary()
        elif choice == "3":
            net_worth()
        elif choice == "4":
            monthly_summary()
        elif choice == "5":
            expense_by_category()
        elif choice == '6':
            break
        else:
            print("Invalid Choice")