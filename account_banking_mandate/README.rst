.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

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

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * no known issues
 
Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/bank-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_banking_mandate%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Alexis de Lattre
* Pedro M. Baeza
* Alexandre Fayolle
* Stéphane Bidoul		<stephane.bidoul@acsone.eu>
* Sergio Teruel (Incaser)		<sergio@incaser.es>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
