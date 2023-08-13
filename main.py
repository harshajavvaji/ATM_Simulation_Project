import os
import asyncio

import datetime

async def write_transaction_to_file(customer, transaction_details, transaction_type, amount, closing_balance):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f"{customer.acc_no}_transactions.txt", "a") as f:
        f.write(f"{timestamp}\t{transaction_details}\t{transaction_type}\t{amount}\t{closing_balance}\n")



class ATM:
    def __init__(self):
        self.cash = {
            2000: 0,
            500: 0,
            100: 0
        }
        self.load_cash_from_file()
    
    def total_amount(self):
        return sum(denom * count for denom, count in self.cash.items())
    
    
    def withdraw_notes(self, amount):
        remaining_amount = amount
        notes = []

        for denom in sorted(self.cash.keys(), reverse=True):
            count = self.cash[denom]
            while count > 0 and remaining_amount >= denom:
                notes.append(denom)
                remaining_amount -= denom
                count -= 1
                self.cash[denom] = count

        if remaining_amount == 0:
            return notes
        else:
            # Rollback notes and return None if unable to vend requested amount
            for denom in notes:
                self.cash[denom] += 1
            return None
    
    def load_cash(self, denomination, count):
        if denomination in self.cash:
            self.cash[denomination] += count

    def save_cash_to_file(self):
        with open("atm_data.txt", "w") as f:
            for denomination, count in self.cash.items():
                f.write(f"{denomination} {count}\n")
    
    def load_cash_from_file(self):
        if os.path.exists("atm_data.txt"):
            with open("atm_data.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    denomination, count = map(int, line.strip().split())
                    self.load_cash(denomination, count)
    
    def save_cash_to_file(self):
        with open("atm_data.txt", "w") as f:
            for denomination, count in self.cash.items():
                f.write(f"{denomination} {count}\n")
    
    def display_atm_balance(self):
        print("\nATM Balance:")
        print("Denomination\tNumber\tValue")
        for denom, count in self.cash.items():
            value = denom * count
            print(f"{denom}\t\t{count}\t{value}")
        total_amount = sum(denom * count for denom, count in self.cash.items())
        print("\nTotal Amount available in the ATM =", total_amount, "₹")

class Customer:
    def __init__(self, acc_no, name, pin, balance):
        self.acc_no = acc_no
        self.name = name
        self.pin = pin
        self.balance = balance

class Bank:
    def __init__(self):
        self.customers = {}
        self.load_customers_from_file()

    def save_customers_to_file(self):
        with open("customer_data.txt", "w") as f:
            for customer in self.customers.values():
                f.write(f"{customer.acc_no},{customer.name},{customer.pin},{customer.balance}\n")
    
    def load_customers_from_file(self):
        if os.path.exists("customer_data.txt"):
            with open("customer_data.txt", "r") as f:
                lines = f.readlines()
                for line in lines:
                    acc_no, name, pin, balance = line.strip().split(",")
                    customer = Customer(acc_no, name, pin, float(balance))
                    self.add_customer(customer)
    
    def add_customer(self, customer):
        self.customers[customer.acc_no] = customer
    
    def get_customer(self, acc_no):
        return self.customers.get(acc_no)

class ATMProcess:
    def __init__(self, atm, bank):
        self.atm = atm
        self.bank = bank
    
    async def mini_statement(self, customer):
        print("\nMini Statement:")
        print("Timestamp\tDescription\tCredit/Debit\tAmount\tClosing Balance")
        
        with open(f"{customer.acc_no}_transactions.txt", "r") as f:
            lines = f.readlines()
            recent_transactions = lines[-10:]  # Get the last 10 transactions
            
            for line in recent_transactions:
                timestamp, transaction_details, transaction_type, amount, closing_balance = line.strip().split("\t")
                print(f"{timestamp}\t{transaction_details}\t{transaction_type}\t{amount}\t{closing_balance}")

    
    def transfer_money(self, sender_acc_no, receiver_acc_no, amount):
        sender = self.bank.get_customer(sender_acc_no)
        receiver = self.bank.get_customer(receiver_acc_no)

        if sender and receiver:
            if amount > 0 and amount <= sender.balance:
                sender.balance -= amount
                receiver.balance += amount
                print("Transfer successful.")
                self.bank.save_customers_to_file()
            else:
                print("Invalid amount or insufficient balance.")
        else:
            print("Invalid account numbers.")
    def validate_customer(self, acc_no, pin):
        customer = self.bank.get_customer(acc_no)
        if customer and customer.pin == pin:
            return True
        return False
    
    def check_balance(self, customer):
        print("Your Balance:", customer.balance, "₹")
    
    def withdraw_money(self, customer, amount):
        if amount < 100 or amount > 10000:
            print("Invalid withdrawal amount. Amount should be between 100 and 10000 ₹.")
            return
        if customer.balance < amount:
            print("Insufficient balance.")
            return
        if amount > self.atm.total_amount():
            print("ATM doesn't have enough cash for this transaction.")
            return
        
        notes = self.atm.withdraw_notes(amount)
        if notes:
            customer.balance -= amount
            self.bank.save_customers_to_file()
            self.atm.save_cash_to_file()
            print(f"Withdrawal successful. Notes vended: {notes}")
            
            transaction_details = "Cash Withdrawal"
            transaction_type = "Debit"
            closing_balance = customer.balance - amount
            asyncio.run(write_transaction_to_file(customer, transaction_details, transaction_type, amount, closing_balance))
    
    def atm_operations(self, acc_no):
        print("\nATM Operations Menu:")
        print("1. Check Balance")
        print("2. Withdraw Money")
        print("3. Transfer Money")
        print("4. Check ATM Balance")
        print("5. Mini Statement")
        
        atm_choice = input("Enter your choice: ")
        customer = self.bank.get_customer(acc_no)
        
        if atm_choice == '1':
            self.check_balance(customer)
        elif atm_choice == '2':
            amount = float(input("Enter amount to withdraw: "))
            self.withdraw_money(customer, amount)
        elif atm_choice == '3':
            receiver_acc_no = input("Enter receiver's account number: ")
            amount = float(input("Enter amount to transfer: "))
            self.transfer_money(acc_no, receiver_acc_no, amount)
        elif atm_choice == '4':
            self.check_atm_balance()
        elif atm_choice == '5':
            customer = self.bank.get_customer(acc_no)
            self.mini_statement(customer)
        
        # Add logic for other ATM operations
        def transfer_money(self, sender, receiver_acc_no, amount):
            sender_customer = self.bank.get_customer(sender)
            receiver_customer = self.bank.get_customer(receiver_acc_no)
            
            if sender_customer.balance < amount:
                print("Insufficient balance for transfer.")
            elif amount < 1000 or amount > 10000:
                print("Invalid transfer amount. Amount should be between 1000 and 10000 ₹.")
            elif receiver_customer:
                sender_customer.balance -= amount
                receiver_customer.balance += amount
                self.bank.save_customers_to_file()
                print("Transfer successful.")
            else:
                print("Receiver's account not found.")

    def check_atm_balance(self):
        self.atm.display_atm_balance()

    def mini_statement(self, customer):
        transactions_file = f"{customer.acc_no}_transactions.txt"
        if os.path.exists(transactions_file):
            with open(transactions_file, "r") as f:
                lines = f.readlines()
                print("Last 10 transactions:")
                print("Transaction Number\tDescription\t\tCredit / Debit\tAmount\tClosing Balance")
                for line in lines[-10:]:
                    transaction = line.strip().split(",")
                    print("\t".join(transaction))
        else:
            print("No transaction history available.")
def main():
    atm = ATM()
    bank = Bank()
    atm_process = ATMProcess(atm, bank)

    while True:
        print("\nMain Menu:")
        print("1. Load Cash to ATM")
        print("2. Show Customer Details")
        print("3. Show ATM Operations")
        choice = input("Enter your choice: ")

        if choice == '1':
            denomination = int(input("Enter denomination (2000/500/100): "))
            count = int(input("Enter count: "))
            if(denomination%2000 == 0 or denomination%500 == 0 or denomination%100 == 0):
                atm.load_cash(denomination, count)
                atm.save_cash_to_file()
                print("Cash loaded successfully.")
            else:
                print("Enter Multiples of 2000 or 500 or 100")
        elif choice == '2':
            acc_no = input("Enter account number: ")
            customer = bank.get_customer(acc_no)
            if customer:
                print("Customer Details:")
                print(f"Name: {customer.name}")
                print(f"Account Number: {customer.acc_no}")
                print(f"Balance: {customer.balance} ₹")
            else:
                print("Customer not found.")
        elif choice == '3':
            acc_no = input("Enter account number: ")
            if atm_process.validate_customer(acc_no, input("Enter PIN: ")):
                atm_process.atm_operations(acc_no)
            else:
                print("Invalid account number or PIN.")
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    # main()
    asyncio.run(main())
