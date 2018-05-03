.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=====================
Account Payment Order
=====================

This module adds support for payment orders and debit orders.

Installation
============

This module depends on:

* account_payment_partner
* base_iban
* document

This modules is part of the OCA/bank-payment suite.

Configuration
=============

This module adds several options on Payment Modes, cf Accounting > Configuration > Management > Payment Modes.

Usage
=====

You can create a Payment Order via the menu Accounting > Payments > Payment Orders and then select the move lines to pay.

You can create a Debit Order via the menu Accounting > Payments > Debit Orders and then select the move lines to debit.

This module also adds a button *Add to Payment Order* on supplier invoices and a button *Add to Debit Order* on customer invoices.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/9.0

Known issues / Roadmap
======================

 * no known issues

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Alexis de Lattre <alexis.delattre@akretion.com>
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
* Jose Maria Alzaga <jose.alzaga@aselcis.com>
* Carlos Dauden

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
