This module supports the functionality to prepare and record Bank Deposit
Tickets, often found in check centric markets like the US. It allows users
to select various customer payments and receipts and bundle them into a
Deposit Ticket. This would be used to support the following activities:
Depositing multiple Checks into your bank account under one deposit ticket,
and Deposit Checks and Cash into your bank account from multiple customer
receipts or payments. This module can be used for any “bank transaction”
centric process including: Paypal, Bank Accounts, and even credit cards –
which tend to deposit funds by bundled transactions versus individual
checks. By combining payments and receipts into deposit tickets, and using
this module to manage the general ledger entries, it will streamline the bank
account statement reconciliation process (defined as: comparing your bank
account transactions versus the recorded transactions in OpenERP for audit
and financial control purposes).

This module also tracks who prepared the Deposit Ticket, and the user who
verified the deposit ticket. In addition to the following: Method of
Deposit (e.g. ATM, Night Drop, Teller, Remote Deposit Capture, Online
Deposit Capture); Bank Tracking number (e.g. TLR#3 BC#47331 REF#94849303938)
; Date of Deposit, Deposit Bag #,  etc.

We recommend users add to their GL Chart of Accounts a new Other Current
Account named Undeposited Funds, as well as a new journal to post payments to
with the Undeposited Funds on the debit side of the transaction.

Why is this module needed?
--------------------------

OpenERP by default is designed for more electronic transaction management –
driven by its heritage in Europe when EFT (electronic) transactions are more
readily used – versus Check centric transactions. In electronic transaction
management – bundled deposits don’t typically occur as payment transactions
typically are displayed individual on statements.

This module is seen as a prerequisite to support efficient Bank Account
Statement Reconciliation found in the US and other countries.
