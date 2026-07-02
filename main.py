from datetime import date, timedelta
import calendar
from logic.accounts import run_accounts
from logic.holdings import run_holdings
from logic.reports import run_reports
from logic.transactions import run_transactions

def last_business_day():
    today = date.today()
    c_year = today.year
    c_month = today.month
    last_day = calendar.monthrange(today.year, today.month)[1]
    
    the_date = date(c_year, c_month, last_day)

    while the_date.weekday() >= 5:
        the_date -= timedelta(days=1)

    return the_date

if __name__ == "__main__":
    while True:
        print("""========== Personal Finance Manager ==========
                1. Manage transactions (like incomes, expenditure, ...)
                2. Manage Accounts
                3. Manage Holdings
                4. View reports
                5. Back
              """)
        choice = input("Select action: ")

        if choice == "1":
            run_transactions()
        elif choice == "2":
            run_accounts()
        elif choice == "3":
            run_holdings()
        elif choice == "4":
            run_reports()
        elif choice == '5':
            break
        else:
            print("Invalid Choice")
    
    
    
    
    