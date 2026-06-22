from datetime import date, timedelta
import calendar


def last_business_day():
    today = date.today()
    c_year = today.year
    c_month = today.month
    last_day = calendar.monthrange(today.year, today.month)[1]
    
    the_date = date(c_year, c_month, last_day)

    while the_date.weekday() >= 5:
        the_date - timedelta(days=1)

    return the_date

class Salary():
    def __init__(self, amount, currency="rupees"):
        self.amount = amount
        self.currency = currency
    

class Bank():
    def __init__(self, name, balance, type="savings"):
        self.name = name
        self.balance = balance
        self.type = type

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount


