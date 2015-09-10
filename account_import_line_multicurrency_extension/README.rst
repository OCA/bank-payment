.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Import Line Multi Currency Extension
============================================

* Improve the view of the import invoice wizard in the bank statement form in order to display more relevant columns. Especially if you work in multi-currency and handle partial payment.

* A column 'Journal currency symbol' has been added just after the amount column to avoid confusion from end-users -> When the bank journal is in foreign currency then the amount column must be filled in that currency.

* When importing lines in currencies amount, amount currency and currency are now correctly handled

A check has been added when pressing 'Reconcile' button: no zero amount are accepted. (since it is obviously an user error)


The following feature have been moved in `bank_statement_import_invoices_fix`
* When lines are imported the reference goes to the communication field (instead of reference of the bank statement line) in order to have a default proposal from the system during the reconciliation process.


Configuration
=============

Nothing


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_import_line_multicurrency_extension%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Vincent Renaville <vincent.renaville@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
