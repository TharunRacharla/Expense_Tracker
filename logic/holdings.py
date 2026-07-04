from db_models.database import get_connection


def add_holding():

    print("\n===== Add Investment =====")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name FROM accounts WHERE account_type='dmat' ORDER BY name""")

    accounts = cur.fetchall()

    if not accounts:
        print("No DMAT accounts found.")
        cur.close()
        conn.close()
        return

    print("\nDMAT Accounts")

    for acc in accounts:
        print(f"{acc[0]}. {acc[1]}")

    try:
        account_id = int(input("\nAccount ID: "))
    except ValueError:
        print("Invalid account.")
        return

    asset_name = input("Asset Name: ")

    print("""
        1. Mutual Fund
        2. Stock
        3. ETF
        4. Gold
        5. Fixed Deposit
        6. Bond
        7. Other
        """)

    asset_types = {"1": "mutual_fund", "2": "stock", "3": "etf", "4": "gold", "5": "fd", "6": "bond", "7": "other"}

    choice = input("Asset Type: ")

    if choice not in asset_types:
        print("Invalid type.")
        return

    asset_type = asset_types[choice]

    try:
        amount_invested = float(input("Amount Invested: ₹"))
        last_updated_value = float(input("Current Value: ₹"))
    except ValueError:
        print("Invalid amount.")
        return

    print("""
        Investment Type

        1. One Time
        2. SIP
        """)

    investment_choice = input("Choice: ")

    if investment_choice == "1":

        investment_type = "one_time"
        sip_amount = None
        sip_frequency = None
        start_date = None

    elif investment_choice == "2":

        investment_type = "sip"

        try:
            sip_amount = float(input("SIP Amount: ₹"))
        except ValueError:
            print("Invalid amount.")
            return

        print("""
        Frequency

        1. Weekly
        2. Monthly
        3. Quarterly
        4. Yearly
        """)

        frequencies = {
            "1": "weekly",
            "2": "monthly",
            "3": "quarterly",
            "4": "yearly"
        }

        freq = input("Frequency: ")

        if freq not in frequencies:
            print("Invalid frequency.")
            return

        sip_frequency = frequencies[freq]

        start_date = input("Start Date (YYYY-MM-DD): ")

    else:

        print("Invalid choice.")
        return

    notes = input("Notes: ")

    updated_on = input("Updated On (YYYY-MM-DD): ")

    cur.execute("""
        INSERT INTO holdings
        (
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
        )
        VALUES
        (?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
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
    ))

    conn.commit()

    cur.close()
    conn.close()

    print("\nInvestment added successfully.")


def view_holdings():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            h.id,
            a.name,
            h.asset_name,
            h.asset_type,
            h.amount_invested,
            h.last_updated_value,
            h.investment_type
        FROM holdings h
        JOIN accounts a
        ON h.account_id=a.id
        ORDER BY h.asset_name
    """)

    rows = cur.fetchall()

    if not rows:
        print("\nNo investments found.")
        return False

    print("\n================ Investments ================\n")

    print(
        f"{'ID':<5}"
        f"{'Account':<20}"
        f"{'Asset':<30}"
        f"{'Invested':>15}"
        f"{'Current':>15}"
        f"{'Gain/Loss':>15}"
    )

    print("-"*105)

    total_invested = 0
    total_current = 0

    for row in rows:

        gain = float(row[5]) - float(row[4])

        total_invested += float(row[4])
        total_current += float(row[5])

        print(
            f"{row[0]:<5}"
            f"{row[1]:<20}"
            f"{row[2]:<30}"
            f"{float(row[4]):>15.2f}"
            f"{float(row[5]):>15.2f}"
            f"{gain:>15.2f}"
        )

    print("-"*105)

    print(f"Total Invested : ₹{total_invested:,.2f}")
    print(f"Last Updated Value  : ₹{total_current:,.2f}")
    print(f"Gain/Loss      : ₹{total_current-total_invested:,.2f}")

    cur.close()
    conn.close()


def update_last_updated_value():
    if view_holdings():
        try:
            holding_id = int(input("\nHolding ID: "))
            last_updated_value = float(input("New Current Value: ₹"))
        except ValueError:
            print("Invalid input.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE holdings
            SET last_updated_value=?,
                updated_on=CURDATE()
            WHERE id=?
        """, (last_updated_value, holding_id))

        conn.commit()

        cur.close()
        conn.close()

        print("Investment updated.")


def delete_holding():

    if view_holdings():
        try:
            holding_id = int(input("\nHolding ID to delete: "))
        except ValueError:
            print("Invalid ID.")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM holdings
            WHERE id=?
        """, (holding_id,))

        conn.commit()

        cur.close()
        conn.close()

        print("Investment deleted.")

def run_holdings():
        while True:

            print("""
                  \n===== Investments =====
                  1. Add Investment
                  2. View Investments
                  3. Update Current Value
                  4. Delete Investment
                  5. Back
                  """)

            choice = input("Choice: ")

            if choice == "1":
                add_holding()

            elif choice == "2":
                view_holdings()

            elif choice == "3":
                update_last_updated_value()

            elif choice == "4":
                delete_holding()

            elif choice == "5":
                break

            else:
                print("Invalid choice.")