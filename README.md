
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/bank-payment&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/bank-payment/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/bank-payment/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/bank-payment/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/bank-payment/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/bank-payment/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/bank-payment)
[![Translation Status](https://translation.odoo-community.org/widgets/bank-payment-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/bank-payment-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# OCA banking payment addons for Odoo

On version 13.0, this project focus on payment interface.
The indentation below indicates the dependency graph of the main modules.

-  `account_payment_order` - Basic export functionality of payment orders

    - `account_banking_sepa_credit_transfer` - Export of payment orders in SEPA format

    - `account_direct_debit` - Debit order infrastructure analogous to Odoo native payment orders

        - `account_banking_sepa_direct_debit` - Export of debit orders in SEPA format

Other features can now be found in these repositories:

 * https://github.com/OCA/bank-statement-import
 * https://github.com/OCA/bank-statement-reconcile

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_banking_mandate](account_banking_mandate/) | 13.0.1.3.0 |  | Banking mandates
[account_banking_pain_base](account_banking_pain_base/) | 13.0.1.0.3 |  | Base module for PAIN file generation
[account_banking_sepa_credit_transfer](account_banking_sepa_credit_transfer/) | 13.0.1.1.2 |  | Create SEPA XML files for Credit Transfers
[account_banking_sepa_direct_debit](account_banking_sepa_direct_debit/) | 13.0.1.2.0 |  | Create SEPA files for Direct Debit
[account_invoice_select_for_payment](account_invoice_select_for_payment/) | 13.0.1.0.0 |  | Account Invoice Select for Payment
[account_payment_mode](account_payment_mode/) | 13.0.1.2.1 |  | Account Payment Mode
[account_payment_order](account_payment_order/) | 13.0.1.6.7 |  | Account Payment Order
[account_payment_order_notification](account_payment_order_notification/) | 13.0.1.0.2 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Account Payment Order Notification
[account_payment_order_return](account_payment_order_return/) | 13.0.1.0.3 |  | Account Payment Order Return
[account_payment_order_tier_validation](account_payment_order_tier_validation/) | 13.0.1.0.0 | [![marcelsavegnago](https://github.com/marcelsavegnago.png?size=30px)](https://github.com/marcelsavegnago) | Extends the functionality of Payment Orders to support a tier validation process.
[account_payment_partner](account_payment_partner/) | 13.0.1.5.0 |  | Adds payment mode on partners and invoices
[account_payment_purchase](account_payment_purchase/) | 13.0.1.0.3 |  | Adds Bank Account and Payment Mode on Purchase Orders
[account_payment_purchase_stock](account_payment_purchase_stock/) | 13.0.1.0.1 |  | Integrate Account Payment Purchase with Stock
[account_payment_sale](account_payment_sale/) | 13.0.1.1.3 |  | Adds payment mode on sale orders

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
