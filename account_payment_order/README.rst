.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Banking - Payments Export Infrastructure
================================================

This module provide an infrastructure to export payment orders.
It includes some bug fixes and obvious enhancements to payment orders that will hopefully land in offical addons one
day.
This technical module provides the base infrastructure to export payment orders
for electronic banking. It provides the following technical features:

* a new payment.mode.type model
* payment.mode now has a mandatory type
* a better implementation of payment_mode.suitable_bank_types() based on
  payment.mode.type
* the "make payment" button launches a wizard depending on the
  payment.mode.type
* a manual payment mode type is provided as an example, with a default "do
  nothing" wizard
  
To enable the use of payment order to collect money for customers,
it adds a payment_order_type (payment|debit) as a basis of direct debit support
(this field becomes visible when account_direct_debit is installed).

Installation
============

This module depends on:

* account_payment_partner
* base_iban

This modules is part of the OCA/bank-payment suite.

Configuration
=============

This module adds several options on Payment Modes, cf Accounting > Configuration > Management > Payment Modes.

Usage
=====

You can create a Payment Order via the menu Accounting > Payments > Payment Orders and then select the move lines to pay.

You can create a Debit Order via the menu Accounting > Payments > Debit Orders and then select the move lines to debit.

This module also adds a button *Add to Payment Order* on supplier invoices and a button *Add to Debit Order* on customer invoices.

Known issues / Roadmap
======================

 * no known issues
 
Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_banking_payment_export%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Alexis de Lattre		
* Pedro M. Baeza     
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Stefan Rijnhart
* Laurent Mignon <laurent.mignon@acsone.eu>
* Alexandre Fayolle
* Danimar Ribeiro
* Erwin van der Ploeg
* Raphaël Valyi
* Sandy Carter
* Angel Moya <angel.moya@domatix.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
