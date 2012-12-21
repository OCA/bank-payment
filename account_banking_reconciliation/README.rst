.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Bank Account Reconciliation
===========================

This module is designed to provide an easy method in which OpenERP accounting users can manually reconcile/validate their financial transactions from their financial institution/transaction providers (e.g. Paypal, A financial institution, google wallet, etc) against OpenERP GL Chart of Account bank accounts.

Users will be able to validate and indicate if a transaction has "Cleared the Bank" using a checkmark on a new Reconcile Financial Account Statement view on each individual financial transaction. Users will also be able to mark transactions on a bank account for future research.

The idea is that as a first step users will manually look at their paper statement and line-by-line check off which financial transactions have cleared the bank in OpenERP using the new Bank Reconciliation Wizard. These changes will be displayed on the  new Reconcile Financial Account Statement tree view screen. This is the process in which many companies reconcile (aka Audit) their bank account statements and accounting system today and represents good segregation of duties.

Users can save their in-process reconciliations.

BACKGROUND
----------

Using the search view filters - users will also be able to effectively sort, filter the transactions on a particular GL Financial Account. This new screen will display the journal items associated with a particular bank account. Several of the field labels have been relabeled to a more common vernacular.

The need for this module is driven by the following: OpenERP's default functionality doesn't support the typical "BANK" account reconciliation process found in many countries (e.g. the US)

Users want to easily record whether bank transactions sent to their bank have "cleared the bank"- definition of "cleared the bank": presented to the bank for payment and paid by the bank - added/subtracted funds on a bank account.

Users want the ability to validate if the bank processed the transactions them correctly (e.g. properly encoded transaction - e.g. company sent a payment of $20.20 to the bank. Was it processed for $20.20?). This can be considered "Auditing the bank statement". We don't assume the bank correctly processed any transaction. 

Users want to understand what payments they've made are still outstanding and have not been paid by the bank. The financial auditing segregation standard of separating the duties of: recording customer payments and making deposits; recording supplier payments and writing checks; and monitoring bank account activity. This segregation of duties is necessary to monitor and help prevent fraud.

Assumptions
-----------

1. Companies using OpenERP have setup a One-to-one relationship between
   their bank accounts and their OpenERP GL accounts. Each bank account
   should have a corresponding GL account that is not shared with another
   account.

   Example:

   OpenERP GL Account #: Corresponding Bank Account
   10100: Bank (AR) Account Checking 5434 (held at Institution A)
   10200: Master Bank Account 2343 (held at Institution A)
   10300: Bank Payable Account Checking 5678 (held at Institution A)
   10400: Bank Payroll Account 6656 (held at Institution B)
   10500: Paypal Account 3343 (held at Paypal)
   10600: Google Wallet Account 6788
   10700: AMEX Corporate Card Account 9989

2. Companies have included a Non-Deposited Funds Account in their GL account
   (typically in current assets in their bank account areas). This account
   is used to store payments that have been recorded in OpenERP - but not
   yet deposited into the financial institution. (NOTE: this account is
   important to have if the user "batches check deposits"- which is the
   process of making a large single deposits of customer payment into the
   bank (e.g. $20,000USD), but it is made up of smaller checks
   (e.g. 20 checks of $1,000 each). Many banks just record the total deposit
   amount ($20,000) and don￢ﾀﾙt provide the breakdown of the individual
   checks that make up the larger deposit. This setup approach enables users
   to drill down and see the individual checks that make up a larger deposit.

Recommendations
---------------

From a cash management and financial control perspective it is recommended
that users establish the following four(4) bank accounts at their financial
institution at a minimum to handle financial transactions.
(NOTE: we recommend users place the last 4 digits of their bank account in
the GL account name of the account. It helps accountants in their management
of the system):

Bank (AR) Account Checking 5434
This is a checking account designated as the account where payments made to
the company are deposited (e.g. a customer payment made by check is
deposited here, or a customer paying by electronic transaction EFT/ACH is
deposited into this GL).

Master Bank Account 2343
This is the master account in which the company keeps the majority of their
funds. Often with the most limited access.

Bank Payable Account Checking  5678
This is a checking account designated for the company to pay their expenses
from. (e.g. Company writes a check to pay a supplier for their office
supplies).

Bank Payroll Account 6656
This is a checking account designated for a company to pay their
employees and payroll.

NOTE: There has been common confusion in the OpenERP community about
managing bank statements in the base OpenERP system. This module
hopes to alleviate this gap and provide users with a sound alternative
to maintain fiscal control, be easy to understand, and allow for
future growth.

Why this approach? Users in OpenERP have several options in which to
record financial transactions that affect the balances of a bank account
(GL Bank Account entries). We believe our approach allows these to work
in conjunction with each other: Import Electronic Bank Statements to enter
payments (this approach follows the philosophy that you first find out
that a transaction has occurred from your bank ￢ﾀﾓ which is very common in
Europe due to the electronic nature of transactions).

Payment Order Payments (using the direct Method) - Payments are instantly
recorded and financial transactions posted into the GL
Voucher Payments - Payments are instantly recorded and financial transactions
posted into the GL Sales Receipts/Refunds
Transfers between accounts (a new module is being developed to help
manage this)
Funds moved from the Undeposited Funds GL account to a Bank Account GL account.
Direct Journal Entries

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/8.0

Known issues / Roadmap
======================

* Extend this module to include a wizard to pre-filter the tree view, and include additional reports for accountants. And include the ability to execute quick entry of common statement related transactions such as recording bank service fees (an Expense), and Interest Income Earned on the bank account  (Income), when allowed by law. Often, companies will print their reconciliation, staple it to their bank statement and file the documents for future review and audit.
* Extend this module to include more information to add further clarity throughout OpenERP for financial transactions, and include the ability to quickly compare an imported bank statement with a GL Bank Account's recorded transaction, including autoreconciling them - and providing the information available for review 

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
bank-payment/issues/new?body=module:%20
account_banking_reconciliation%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Nova Point Group
* Mathieu Benoit <mathieu.benoit@savoirfairelinux.com>
* Vincent Vinet <vincent.vinet@savoirfairelinux.com>

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
