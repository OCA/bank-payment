.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Prevent the usage of payments from invoices
===========================================

This add-on disables the "Register Payment" button on
customer invoices and the "Pay" button on supplier invoices.

It also disables the payments-related menus entries such as
"Customer Payments", "Supplier Payments"

More precisely, this module adds a group "Payments for Invoices"
and only users in that group see these buttons and menus.

Installation
============

This module depends on :

 * account

This modules are parts of the OCA/bank-payment suite.

Configuration
=============

Use new group Payment for Invoices to allow make payments

Usage
=====

See above the description of the module.


For further information, please visit:

 * https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_voucher_killer%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Nicolas Bessi (camptocamp)
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Anthony Muschang <anthony.muschang@acsone.eu>
* Yannick Vaucher
* Cristian Salamea <cs@prisehub.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
