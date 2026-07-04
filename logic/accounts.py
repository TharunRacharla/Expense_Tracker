# accounts.py

from db_models.database import get_connection


def add_account():
    """Add a new account."""

    print("\n=== Add Account (like bank name)===")

    name = input("Account Name: ")

    print("\nAccount Types")
    print("1. Savings")
    print("2. Current")
    print("3. Credit Card")
    print("4. Cash")
    print("5. Wallet")
    print("6. DEMAT")

    account_types = {
        "1": "savings",
        "2": "current",
        "3": "credit_card",
        "4": "cash",
        "5": "wallet",
        "6": "dmat"
    }

    choice = input("Choose account type: ")

    if choice not in account_types:
        print("Invalid account type. Select from the options above.")
        return

    account_type = account_types[choice]

    try:
        if account_type == "credit_card":
            opening_balance = -float(input("Current Outstanding:  "))
        else:
            opening_balance = float(input("Opening Balance: "))
    except ValueError:
        print("Invalid balance.")
        return

    credit_limit = None

    if account_type == "credit_card":
        try:
            credit_limit = float(input("Credit Limit: "))
        except ValueError:
            print("Invalid credit limit.")
            return

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO accounts
        (
            name,
            account_type,
            opening_balance,
            current_balance,
            credit_limit
        )
        VALUES
        (?,?,?,?,?)
    """

    cursor.execute(
        query,
        (
            name,
            account_type,
            opening_balance,
            opening_balance,
            credit_limit
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("\nAccount added successfully.")


def view_accounts(get_attribute=None):
    """Display all accounts."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            account_type,
            current_balance
        FROM accounts
        ORDER BY id
    """)

    rows = cursor.fetchall()

    if not rows:
        print("\nNo accounts found.")
        return False

    print("\n==============================")
    print("Accounts")
    print("==============================")

    print(
        f"{'ID':<5}"
        f"{'Name':<20}"
        f"{'Type':<15}"
        f"{'Balance':>12}"
    )

    print("-" * 55)

    for row in rows:
        print(
            f"{row[0]:<5}"
            f"{row[1]:<20}"
            f"{row[2]:<15}"
            f"₹{float(row[3]):>10.2f}"
        )

    cursor.close()
    conn.close()

    if get_attribute == "id":
        ids =  [row[0] for row in rows]
        return ids
        


def get_account(account_id):
    """Return one account."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM accounts
        WHERE id=?
    """, (account_id,))

    account = cursor.fetchone()

    cursor.close()
    conn.close()

    return account


def update_balance(account_id, amount, operation):
    """
    operation:
        '+' increase balance
        '-' decrease balance
    """

    conn = get_connection()
    cursor = conn.cursor()

    if operation == "+":
        cursor.execute("""
            UPDATE accounts
            SET current_balance =
                current_balance + ?
            WHERE id=?
        """, (amount, account_id))

    elif operation == "-":
        cursor.execute("""
            UPDATE accounts
            SET current_balance =
                current_balance - ?
            WHERE id=?
        """, (amount, account_id))

    conn.commit()

    cursor.close()
    conn.close()


def delete_account():
    """Delete an account."""

    view_accounts()

    try:
        account_id = int(input("\nEnter Account ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM accounts
        WHERE id=?
    """, (account_id,))

    conn.commit()

    cursor.close()
    conn.close()

    print("Account deleted.")


def run_accounts():
    while True:

        print("\n===== Accounts =====")

        print("1. Add Account")
        print("2. View Accounts")
        print("3. Delete Account")
        print("4. Exit")

        choice = input("Choice: ")

        if choice == "1":
            add_account()

        elif choice == "2":
            view_accounts()

        elif choice == "3":
            delete_account()

        elif choice == "4":
            break

        else:
            print("Invalid option.")