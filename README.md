[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/173/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-bank-payment-173)
[![Build Status](https://travis-ci.org/OCA/bank-payment.svg?branch=13.0)](https://travis-ci.org/OCA/bank-payment)
[![Coverage Status](https://coveralls.io/repos/OCA/bank-payment/badge.png?branch=13.0)](https://coveralls.io/r/OCA/bank-payment?branch=13.0)

OCA banking payment addons for Odoo
===================================

On version 13.0, this project focus on payment interface. The indentation below
indicates the dependency graph of the main modules.

-  `account_payment_order` - Basic export functionality of payment orders

    - `account_banking_sepa_credit_transfer` - Export of payment orders in SEPA format

    - `account_direct_debit` - Debit order infrastructure analogous to Odoo native payment orders

        - `account_banking_sepa_direct_debit` - Export of debit orders in SEPA format

Other features can now be found in these repositories:

 * https://github.com/OCA/bank-statement-import
 * https://github.com/OCA/bank-statement-reconcile


Contributing
------------
Do you want to contribute? Please read our [contributing guidelines](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md).

----

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

http://odoo-community.org/
