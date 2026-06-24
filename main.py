from datetime import date, timedelta
import calendar


def last_business_day():
    today = date.today()
    c_year = today.year
    c_month = today.month
    last_day = calendar.monthrange(today.year, today.month)[1]
    
    the_date = date(c_year, c_month, last_day)

    while the_date.weekday() >= 5:
        the_date -= timedelta(days=1)

    return the_date

class Account():
    def __init__(self, name, account_type="savings", balance=0):
        self.name = name
        self.balance = balance
        self.account_type = account_type

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.account_type}) "
            f"₹{self.balance}"
        )

class CreditCard(Account):
    def __init__(self, name, credit_limit, outstanding=0):
        super().__init__(name, "credit_card", -outstanding)

        self.credit_limit = credit_limit
        self.outstanding = outstanding

    def spend(self, amount):
        self.outstanding += amount

    def pay_bill(self, amount):
        self.outstanding -= amount