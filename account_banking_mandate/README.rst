.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=======================
Account Banking Mandate
=======================

This module adds a generic model for banking mandates.
These mandates can be specialized to fit any banking mandates (such as sepa or lsv).

A banking mandate is attached to a bank account and represents an
authorization that the bank account owner gives to a company for a
specific operation (such as direct debit).
You can setup mandates from the accounting menu or directly from a bank
account.

Installation
============

This module depends on :
* account_payment

This module is part of the OCA/bank-payment suite.

Configuration
=============

TODO

Usage
=====

To use this module, see menu "Accounting > payment > SEPA direct debit mandates"

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

* Alexis de Lattre <alexis.delattre@akretion.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Alexandre Fayolle
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Sergio Teruel <sergio.teruel@tecnativa.com>
* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Carlos Dauden <carlos.dauden@tecnativa.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
