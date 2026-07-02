from datetime import datetime
from logic.accounts import view_accounts, update_balance
from db_models.database import get_connection

def add_transaction(txn_type):
    print(f"\n==== Add {txn_type.title()} ===")
    view_accounts()

    try:
        account_id = int(input("\nAccount ID: "))
    except ValueError:
        print("Invalid account")
        return
    
    try:
        amount =  float(input("Amount: "))
    except ValueError:
        print("Invalid amount")
        return
    
    category = input("Category: ")
    description = input("Description: ")

    date_str = input("Date (YYYY-MM-DD HH:MM): ")

    try:
        txn_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid Date")
        return
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO transactions (account_id, txn_date, txn_type, category, description, amount) VALUES (%s, %s, %s, %s, %s, %s)", 
                (account_id, txn_date, txn_type, category, description, amount))
    
    conn.commit()
    cur.close()
    conn.close()

    if txn_type == "income":
        update_balance(account_id, amount, "+")
    else:
        update_balance(account_id, amount, "-")

def view_transactions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            t.id,
            t.txn_date,
            a1.name,
            a2.name,
            t.txn_type,
            t.category,
            t.amount,
            t.description
        FROM transactions t
        JOIN accounts a1
        ON t.account_id=a1.id
        LEFT JOIN accounts a2
        ON t.destination_account_id = a2.id
        ORDER BY t.txn_date DESC
    """)

    rows = cursor.fetchall()

    print("\nTransactions")
    print("-"*90)

    print(
        f"{'ID':<5}"
        f"{'Date':<20}"
        f"{'Account':<35}"
        f"{'Type':<12}"
        f"{'Amount':>12}"
        f"\t{'Description':<50}"
    )

    print("-"*90)

    for row in rows:

        source = row[2]
        destination = row[3] if row[3] else "-"

        if row[4] == "transfer":
            account = f"{source} -> {destination}"
        else:
            account = source

        print(
            f"{row[0]:<5}"
            f"{str(row[1]):<20}"
            f"{account:<35}"
            f"{row[4]:<12}"
            f"₹{float(row[6]):>10.2f}"
            f"\t{row[7]}"
        )

    cursor.close()
    conn.close()

def add_income():
    add_transaction("income")


def add_expense():
    add_transaction("expense")


def transfer_money():

    print("\n===== Transfer Money =====")

    ids = view_accounts(get_attribute="id")

    try:
        from_account = int(input("\nTransfer FROM Account ID: "))
        if from_account not in ids:
            print("account invalid, select from above accounts.")
        to_account = int(input("Transfer TO Account ID: "))
        if to_account not in ids:
            print("Account invalid, selct from above accounts.")

    except ValueError:
        print("Invalid account.")
        return

    if from_account == to_account:
        print("Source and destination cannot be the same.")
        return

    try:
        amount = float(input("Amount: ₹"))
    except ValueError:
        print("Invalid amount.")
        return

    description = input("Description: ")

    date_str = input("Date (YYYY-MM-DD HH:MM): ")

    try:
        txn_date = datetime.strptime(
            date_str,
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        print("Invalid date.")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions
        (
            account_id,
            destination_account_id,
            txn_date,
            txn_type,
            category,
            description,
            amount
        )
        VALUES
        (%s,%s,%s,'transfer','Transfer',%s,%s)
    """,
    (
        from_account,
        to_account,
        txn_date,
        description,
        amount
    ))

    conn.commit()

    cur.close()
    conn.close()

    update_balance(from_account, amount, "-")
    update_balance(to_account, amount, "+")

    print("Transfer completed.")


def run_transactions():
    while True:
                
        print("\nTransactions")

        print("1. Add Income or Reimbursents")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. Transfer Money")
        print("5. Back")

        choice = input("Choice: ")

        if choice == "1":
            add_income()

        elif choice == "2":
            add_expense()

        elif choice == "3":
            view_transactions()

        elif choice == "4":
            transfer_money()
        
        elif choice == '5':
            break

        else:
            print("Invalid Choice")