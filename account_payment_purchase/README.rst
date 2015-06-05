.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Payment Purchase
========================

This module adds 2 fields on purchase orders: *Bank Account* and *Payment
Mode*. These fields are copied from partner to purchase order and then from
purchase order to supplier invoice.

This module is similar to the *purchase_payment* module; the main difference
is that it doesn't depend on the *account_payment_extension* module (it's not
the only module to conflict with *account_payment_extension*; all the SEPA
modules in the banking addons conflict with *account_payment_extension*).

Installation
============

This module depends on :
- purchase
- account_payment_partner

This module is part of the OCA/bank-payment suite.

Configuration
=============

There is nothing to configure.

Usage
=====

You are able to add a payment mode directly on a partner.
This payment mode is automatically associated to the purchase order, then on related invoice. 
This default value could be change in a draft purchase or draft invoice.
When you create an payment order, only invoices related to chosen payment mode are displayed.
Invoices without any payment mode are displayed to.


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
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_payment_purchase%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza
* Alexis de Lattre
* Alexandre Fayolle
* Danimar Ribeiro
* Raphaël Valyi
     
Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
