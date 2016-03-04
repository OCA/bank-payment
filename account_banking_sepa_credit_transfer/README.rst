.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Banking SEPA Credit Transfer
====================================

Module to export payment orders in SEPA XML file format.

SEPA PAIN (PAyment INitiation) is the new european standard for
Customer-to-Bank payment instructions. This module implements SEPA Credit
Transfer (SCT), more specifically PAIN versions 001.001.02, 001.001.03,
001.001.04 and 001.001.05. It is part of the ISO 20022 standard, available on
http://www.iso20022.org.

The Implementation Guidelines for SEPA Credit Transfer published by the
European Payments Council (http://http://www.europeanpaymentscouncil.eu) use
PAIN version 001.001.03, so it's probably the version of PAIN that you should
try first.

It also includes pain.001.003.03 which is used in Germany instead of 001.001.03.
You can read more about this here (only in german language):
http://www.ebics.de/startseite/

Installation
============

This module depends on :
* account_banking_pain_base

This module is part of the OCA/bank-payment suite.

Configuration
=============

No specific configuration.

Usage
=====

* You need to choose first an SEPA export type on a payment mode.

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
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_banking_sepa_credit_transfer%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre
* Pedro M. Baeza
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Stefan Rijnhart
* Julien Laloux
* Alexandre Fayolle
* Raphaël Valyi
* Erwin van der Ploeg
* Sandy Carter
* Antonio Espinosa <antonioea@antiun.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
