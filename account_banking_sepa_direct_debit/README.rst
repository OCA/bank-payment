.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Banking SEPA Direct Debit
=================================

Create SEPA files for Direct Debit

Module to export direct debit payment orders in SEPA XML file format.

SEPA PAIN (PAyment INitiation) is the new european standard for
Customer-to-Bank payment instructions. This module implements SEPA Direct
Debit (SDD), more specifically PAIN versions 008.001.02, 008.001.03 and
008.001.04. It is part of the ISO 20022 standard, available on
http://www.iso20022.org.

The Implementation Guidelines for SEPA Direct Debit published by the European
Payments Council (http://http://www.europeanpaymentscouncil.eu) use PAIN
version 008.001.02. So if you don't know which version your bank supports, you
should try version 008.001.02 first.

Installation
============

This module depends on :
* account_direct_debit
* account_banking_pain_base',
* account_banking_mandate

This module is part of the OCA/bank-payment suite.

Configuration
=============

To configure this module, you need to:

 * Create a payment mode and select an export type related to debit order ( eg. "SEPA direct debit ...")

Usage
=====

To use this module, you must select this payment mode on a direct debit order (Menu :Accounting > Payment > Direct Debit orders)

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * No known issues

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_banking_sepa_direct_debit%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre
* Pedro M. Baeza
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Alexandre Fayolle
* Raphaël Valyi
* Sandy Carter
* Antonio Espinosa <antonioea@antiun.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
