.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Payment Partner
=======================

This module adds severals fields :

* the *Supplier Payment Mode* and *Customer Payment Mode* on Partners,

* the *Payment Mode* on Invoices.

On a Payment Order, in the wizard *Select Invoices to Pay*, the invoices will
be filtered per Payment Mode.

Installation
============

This module depends on :
* account_banking_payment_export

This module is part of the OCA/bank-payment suite.

Configuration
=============

There is nothing to configure.

Usage
=====

You are able to add a payment mode directly on a partner.
This payment mode is automatically associated to the invoice related to the partner. This default value could be change in a draft invoice.
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
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_payment_partner%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Pedro M. Baeza
* Alexis de Lattre
* Raphaël Valyi
* Stefan Rijnhart (Therp)
* Alexandre Fayolle
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Danimar Ribeiro
* Angel Moya <angel.moya@domatix.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
