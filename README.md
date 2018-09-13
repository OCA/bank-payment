[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/173/10.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-bank-payment-173)
[![Build Status](https://travis-ci.org/OCA/bank-payment.svg?branch=10.0)](https://travis-ci.org/OCA/bank-payment)
[![Coverage Status](https://coveralls.io/repos/OCA/bank-payment/badge.png?branch=10.0)](https://coveralls.io/r/OCA/bank-payment?branch=10.0)

OCA banking payment addons for Odoo
===================================

On version 10.0, this project focus on payment interface. The indentation below 
indicates the dependency graph of the main modules.

- account_banking_payment_export - Basic export functionality of payment orders

    - account_banking_sepa_credit_transfer - Export of payment orders in SEPA format

    - account_direct_debit - Debit order infrastructure analogous to Odoo native payment orders

        - account_banking_sepa_direct_debit - Export of debit orders in SEPA format
        
Other features can now be found in these repositories:

 * https://github.com/OCA/bank-statement-import
 * https://github.com/OCA/bank-statement-reconcile

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[account_banking_mandate](account_banking_mandate/) | 10.0.1.1.6 | Banking mandates
[account_banking_mandate_sale](account_banking_mandate_sale/) | 10.0.1.0.1 | Adds mandates on sale orders
[account_banking_pain_base](account_banking_pain_base/) | 10.0.1.1.1 | Base module for PAIN file generation
[account_banking_sepa_credit_transfer](account_banking_sepa_credit_transfer/) | 10.0.1.0.0 | Create SEPA XML files for Credit Transfers
[account_banking_sepa_direct_debit](account_banking_sepa_direct_debit/) | 10.0.1.1.2 | Create SEPA files for Direct Debit
[account_payment_line_cancel](account_payment_line_cancel/) | 10.0.1.0.0 | Account payment line cancel
[account_payment_mode](account_payment_mode/) | 10.0.1.0.2 | Account Payment Mode
[account_payment_order](account_payment_order/) | 10.0.1.6.0 | Account Payment Order
[account_payment_partner](account_payment_partner/) | 10.0.1.1.2 | Adds payment mode on partners and invoices
[account_payment_purchase](account_payment_purchase/) | 10.0.1.0.0 | Adds Bank Account and Payment Mode on Purchase Orders
[account_payment_sale](account_payment_sale/) | 10.0.1.1.0 | Adds payment mode on sale orders
[account_voucher_killer](account_voucher_killer/) | 10.0.1.0.0 | Accounting Payment Access


Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_banking_tests](account_banking_tests/) | 8.0.0.1.0 (unported) | Banking Addons - Tests
[account_import_line_multicurrency_extension](account_import_line_multicurrency_extension/) | 8.0.1.1.0 (unported) | Add an improved view for move line import in bank statement
[account_payment_blocking](account_payment_blocking/) | 8.0.1.0.0 (unported) | Prevent invoices under litigation to be proposed in payment orders.
[account_payment_mode_term](account_payment_mode_term/) | 8.0.0.1.2 (unported) | Account Banking - Payments Term Filter
[bank_statement_instant_voucher](bank_statement_instant_voucher/) | 1.0r028 (unported) | Bank statement instant voucher
[portal_payment_mode](portal_payment_mode/) | 8.0.1.0.0 (unported) | Adds payment mode ACL's for portal users

[//]: # (end addons)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
