[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/173/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-bank-payment-173)
[![Build Status](https://travis-ci.org/OCA/bank-payment.svg?branch=8.0)](https://travis-ci.org/OCA/bank-payment)
[![Coverage Status](https://coveralls.io/repos/OCA/bank-payment/badge.png?branch=8.0)](https://coveralls.io/r/OCA/bank-payment?branch=8.0)

OCA banking payment addons for Odoo
===================================

On version 8.0, this project focus on payment interface. The indentation below 
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
[account_banking_mandate](account_banking_mandate/) | 8.0.0.2.1 | Banking mandates
[account_banking_pain_base](account_banking_pain_base/) | 8.0.0.4.0 | Base module for PAIN file generation
[account_banking_payment_export](account_banking_payment_export/) | 8.0.0.3.0 | Account Banking - Payments Export Infrastructure
[account_banking_payment_transfer](account_banking_payment_transfer/) | 8.0.0.3.1 | Account Banking - Payments Transfer Account
[account_banking_sepa_credit_transfer](account_banking_sepa_credit_transfer/) | 8.0.0.5.0 | Create SEPA XML files for Credit Transfers
[account_banking_sepa_direct_debit](account_banking_sepa_direct_debit/) | 8.0.0.5.0 | Create SEPA files for Direct Debit
[account_banking_tests](account_banking_tests/) | 8.0.0.1.0 | Banking Addons - Tests
[account_direct_debit](account_direct_debit/) | 8.0.2.1.0 | Direct Debit
[account_import_line_multicurrency_extension](account_import_line_multicurrency_extension/) | 8.0.1.1.0 | Add an improved view for move line import in bank statement
[account_payment_blocking](account_payment_blocking/) | 8.0.1.0.0 | Prevent invoices under litigation to be proposed in payment orders.
[account_payment_include_draft_move](account_payment_include_draft_move/) | 8.0.1.0.0 | Account Payment Draft Move
[account_payment_mode_term](account_payment_mode_term/) | 8.0.0.1.2 | Account Banking - Payments Term Filter
[account_payment_partner](account_payment_partner/) | 8.0.0.2.0 | Adds payment mode on partners and invoices
[account_payment_purchase](account_payment_purchase/) | 8.0.1.0.0 | Adds Bank Account and Payment Mode on Purchase Orders
[account_payment_sale](account_payment_sale/) | 8.0.1.0.0 | Adds payment mode on sale orders
[account_payment_sale_stock](account_payment_sale_stock/) | 8.0.1.0.0 | Manage payment mode when invoicing a sale from picking
[account_payment_transfer_reconcile_batch](account_payment_transfer_reconcile_batch/) | 8.0.1.0.0 | Batch Reconciliation for transfer moves
[account_voucher_killer](account_voucher_killer/) | 8.0.1.0.0 | Accounting voucher killer
[portal_payment_mode](portal_payment_mode/) | 8.0.1.0.0 | Adds payment mode ACL's for portal users


Unported addons
---------------
addon | version | summary
--- | --- | ---
[bank_statement_instant_voucher](bank_statement_instant_voucher/) | 1.0r028 (unported) | Bank statement instant voucher

[//]: # (end addons)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
