.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Bank Deposit Ticket
===================

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

We recommend users add to their GL Chart of Accounts a new Other Current Account named Undeposited Funds, as well as a new journal to post payments to with the Undeposited Funds on the debit side of the transaction.

Why is this module needed?
--------------------------

OpenERP by default is designed for more electronic transaction management – driven by its heritage in Europe when EFT (electronic) transactions are more readily used – versus Check centric transactions. In electronic transaction management – bundled deposits don’t typically occur as payment transactions typically are displayed individual on statements.

This module is seen as a prerequisite to support efficient Bank Account Statement Reconciliation found in the US and other countries.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/8.0

Known issues / Roadmap
======================

* Include the ability to track deposits NOT using the Undeposited Funds GL account.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
bank-payment/issues/new?body=module:%20
account_banking_make_deposit%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Nova Point Group
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
