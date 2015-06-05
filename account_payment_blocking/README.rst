.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Block payment of invoices
=========================

This module was written to extend the functionality of payment orders
to prevent invoices under litigation to be presented for inclusion in payment orders.

This module uses the 'blocked' flag that is present on journal items
to filter out lines proposed in payment orders.

In addition it exposes this flag on the supplier invoice form
so it is easier to block an invoice.

Installation
============

This module depends on 
* account_banking_payment_export

This module is part of the OCA/bank-payment suite.

Configuration
=============

There is nothing to configure.

Usage
=====

To use this module, set the "Blocked" flag on supplier invoices
or on payable/receivable journal items.

These invoices will not be proposed for inclusion in payment orders.


For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * No known issues.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_payment_blocking%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

