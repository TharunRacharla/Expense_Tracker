import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_expense():
    date = input("Date (YYYY-MM-DD): ")
    category = input("Category: ")
    description = input("Description: ")
    try:
        amount = float(input("Amount: ₹"))
    except ValueError:
        print("Invalid Amount")
        return
    
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO expenses (expense_date, category, amount, description) VALUES (%s, %s, %s, %s)"

    cursor.execute(query, (date, category, amount, description))
    conn.commi()
    cursor.close()
    conn.close()

    print("expense added successfully")

def view_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execut("""
                SELECT * from expenses
            """)
    
    rows = cursor.fetchall()

    print(f"\n Expenses")
    print("-" * 80)
    print(
        f"{'ID':<5}{'Date':<12}"
        f"{'Category':<15}"
        f"{'Amount':>10}"
        f"{'Description':<25}"
    )
    print("-" * 80)

    for row in rows:
        print(
            f"{row[0]:<5}"
            f"{str(row[1]):<12}"
            f"{row[2]:<15}"
            f"₹{float(row[4]):>8.2f}"
            f"{row[3]:<25}"
        )

    cursor.close()
    conn.close()

def show_total():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execut("SELECT sum(amount) FROM expenses")

    total = cursor.fetchone()[0] or 0

    print(f"\n Total expenses: ₹{total}")
    cursor.close()
    conn.close()

def monthly_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT DATE_FORMT(expense_date, '%Y-%m') AS Month, sum(amount)
                   FROM expenses
                   GROUP by Month
                   ORDER by Month Desc
                """)
    
    results = cursor.fetchall()

    print("\nMonthly Summary")
    print("-" * 30)

    for month, total in results:
        print(f"{month}: ₹{float(total):.2f}")

    cursor.close()
    conn.close()

def category_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                SELECT category, sum(amount)
                FROM expenses
                GROUP by category
                ORDER BY sum(amount) DESC
            """)
    
    results = cursor.fetchall()

    print("\n Category wise Summary")
    print("-" * 30)

    for category, total in results:
        print(f"{category:<20}: ₹{float(total):.2f}")

    cursor.close()
    conn.close()

def main():
    while True:
        print("\n===== Expense Tracker =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Expenses")
        print("4. Monthly Summary")
        print("5. Category Summary")
        print("6. Exit")

        choice = input("Select option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_total()
        elif choice == "4":
            monthly_summary()
        elif choice == "5":
            category_summary()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
        