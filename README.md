[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/173/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-bank-payment-173)
[![Build Status](https://travis-ci.com/OCA/bank-payment.svg?branch=13.0)](https://travis-ci.com/OCA/bank-payment)
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

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
