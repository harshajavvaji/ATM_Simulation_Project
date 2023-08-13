# ATM_Simulation_Project

This is a ATM simulation project developed in Python that allows users to perform various banking operations through a command-line interface. The project utilizes Python's asynchronous capabilities to handle multiple users concurrently and perform tasks like checking balance, withdrawing money, transferring money, and viewing mini statements.

# Features
- Load cash into the ATM with different denominations (2000, 500, 100).
- Retrieve customer details including name, account number, and balance.
- Perform ATM operations:
  - Check account balance.
  - Withdraw money (with proper note denomination).
  - Transfer money between accounts.
  - View ATM balance.
  - Get a mini statement of recent transactions.
- Utilizes asynchronous programming for concurrent operations.
- Data is saved to files: `atm_data.txt` for ATM balance and `customer_data.txt` for customer information.
- Transactions are recorded in files with a timestamp for future reference.


**Requirements**
- Python 3.x

**Author**
-Harsha Vardhan
