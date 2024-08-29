import json
import datetime

with open('balances.json', 'r') as file:
    account = json.load(file)

balance = float(account.get('balance', 0.0))


def main():
    print("Welcome to your personal finance tracker. \n In this application you will be able to peek at an account summary, \n add a deposit to your account, create a new expense, \n create a new bill, adjust an existing bill, \n add to your savings, withdraw from your savings, \n and access an expense calculator to view your spending limit for the pay period.")
    options = {'summary' : account_summary
        , 'deposit': add_money
        , 'expense' : create_expense
        , 'bill' : create_bill
        , 'calculator': expense_calculator
        , 'adjust_bill' : adjust_bill
        , 'add_savings' : add_savings
        , 'withdraw_savings' : withdraw_savings}
    if account.get('account_setup'):
        while True:
            action = input("What would you like to do? (summary, deposit, expense, bill, calculator, adjust_bill, add_savings, withdraw_savings) ").lower()
            if options[action]:
                break
            else:
                print("Please input a valid option from the list.")
        
    else:
        account_setup()

    options[action]

def account_setup():
    #add pay cycle and payday
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    while True:
        date = input("Please enter the abbreviated day of the week you get paid:")
        if date.lower() in days:
            break
        else:
            print ("Please enter the proper three letter abbreviation of your payday")
    while True:
        paycycle = input("Please input the frequency of you pay cycle (weekly or bi-weekly) :")
        if paycycle == 'weekly' or paycycle == 'bi-weekly':
            break
        else:
            print("Please input a proper paycycle (weekly or bi-weekly)")
    while True:
        savings = input("Would you like to setup a savings goal? (y/n)").lower()
        if savings == 'y':
            savings_goals()
            break
        elif savings == 'n':
            break
        else: 
            print("Please enter a valid answer (y/n)")
    
    pay_schedule = {'paycycle':paycycle , 'payday' : date}
    account['pay_schedule'] = pay_schedule
    account['account_setup'] = "Account setup complete"
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)

        


def account_summary(balance):
    today =datetime.date.today().strftime("%d")
    bills_due  = []
    if account['bills']:
        for bills in account['bills']:
            if bills['duedate'] >= today:
                bills_due.append(bills)
    print("Your current balance is:" + balance)
    print(f"Your bills still due this month are")
    if bills_due:
        for bill in bills_due:
            print (f"{bill['title']} on {bill['duedate']}")
    

def add_money(balance):
    while True:
        try:
            money = float(input("Please input a balance to add to your account:"))
        except ValueError:
            print("Invalid input, please input a number value")
        break
    balance += money
    account['balance'] = balance
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)




def create_expense(balance):
    category = input("Please input a category for your expense:").lower()
    expense_date = datetime.date.today().isoformat()
    while True:
        try:
            cost = float(input("Please input the cost of your expense:"))
        except ValueError:
            print("Invalid input, please input a number value")
        break
    expense = {'date': expense_date, 'cost': cost}
    account['categories'] = account.get('categories', {})
    account['categories'][category] = account['categories'].get(category, [])

    account['categories'][category].append(expense)
    balance -= cost
    account['balance'] = balance
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)



def create_bill(balance):
    title = input("Please input a title for your bill:").lower()
    while True:
        try:
            cost = float(input("Please input the cost of this bill:"))
        except ValueError:
            print("Invalid input, please input a number value")
        break
    while True:
        date = input("Please input the day of the month this bill will be charged (dd):")
        if len(date) == 2 and date.isdigit():
            break
        else:
            print("Please enter date in formate (dd)")

    bill = {'title': title, 'cost' : cost, 'duedate' : date}
    account['bills'] = account.get('bills', [])
    if any(b['title'] == title for b in account["bills"]):
        print("Bill already in database")
    else:
        account['bills'].append(bill)

    today =datetime.date.today().strftime("%d")
    if date == today:
        balance -= cost
    
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)

def adjust_bill():
    bill = input("What bill would you like to adjust?:").lower()
    while True:
        try:
            cost = float(input("Please input the new cost of this bill:"))
        except ValueError:
            print("Invalid input, please input a number value")
        break
    for b in account['bills']:
        if b['title'] == bill:
            b['cost'] = cost
        else:
            print("Bill not found")
    with open('balances.json', 'w' ) as file:
        json.dump(account, file, indent=4)


def expense_calculator(balance):
    days = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7}
    thirty = ['apr','jun', 'sept', 'nov']
    thirtyone = ['jan', 'mar', 'may', 'july', 'aug', 'oct', 'dec']
    pay_cycle = account['payschedule']['paycycle']
    payday = account['payschedule']['payday']
    today =datetime.date.today().strftime("%a")
    today_date =datetime.date.today().strftime("%d")
    if days[payday] < days[today]:
        days_until_pay = 7 - days[today] + days[payday]
    elif days[payday] == days[today]:
        days_until_pay = 7
    else: 
        days_until_pay = 7 - days[today]
    if pay_cycle == "bi-weekly":
        days_until_pay += 7
    bills_due = []
    bill_expenses = 0
    this_month = datetime.date.today().strftime("%b")
    month_length = 0
    if this_month in thirty:
        month_length = 30
    elif this_month in thirtyone:
        month_length = 31
    else:
        month_length = 28
    for b in account['bills']:
        if today_date + days_until_pay > month_length:
            if b['duedate'] >= today_date or b['duedate'] < (today_date + days_until_pay) - month_length:
                bills_due.append(b)
        else:
            if b['duedate'] >= today_date and b['duedate']< today_date + days_until_pay:
                bills_due.append(b)
    for bills in bills_due:
        bill_expenses += bills['cost']
    spending_money = balance - bill_expenses
    account['spending_money'] = spending_money
    print(f"Your spending allowance for this week is {spending_money:.2f} and your next payday is in {days_until_pay} days. Your bills due until the next paday are")
    if bills_due:
        for bill in bills_due:
            print(f"{bill['title']}, for {bill['cost']} on {this_month} {bill['duedate']}")
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)


    


def savings_goals():
    while True:
        try:
            savings_level = float(input("On a scale of 1-5 how aggresive would you like to save?"))
            if savings_level >= 1 and savings_level <= 5:
                break
            else:
                print("Please enter a value from 1-5")
        except ValueError:
            print("Please enter a value from 1-5")
    spending_money = account['spending_money']
    savings = spending_money * (savings_level * 0.1)
    print(f"Your amount to save this pay period is {savings}")
    account['amount_to_save'] = savings
    with open('balances.json' , ' w' ) as file:
        json.dump(account, file, indent=4)

def add_savings():
    while True:
        add_to_savings = input("How much would you like to add to your savings? (Input a numeric value or goal to add the full goal amount)")
        if add_to_savings.isdigit():
            account['savings'] += add_to_savings
            break
        elif add_to_savings.lower() == 'goal':
            account['savings'] += account['amount_to_save']
            break
        else:
            print("PLease input a valid response")
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)

def withdraw_savings():
    while True:
        try:
            withdraw_amount = int(input("What amount would you like to withdraw"))
            break
        except ValueError:
            print("Please input a number value")
    account['savings'] -= withdraw_amount
    with open('balances.json', 'w') as file:
        json.dump(account, file, indent=4)



    
    



if __name__ == '__main__':
    main()
