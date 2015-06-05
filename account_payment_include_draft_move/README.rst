.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Account Payment Draft Move
==========================

Include draft moves in account payments

Add payment order line from unposted move lines.
With account_default_draft_move, this module allows to add move lines
to payment orders before making the periodic process of posting all moves.

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

A new payment order allow to select draft journal items related to an invoice.

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
`here <https://github.com/OCA/bank-payment/issues/new?body=module:%20account_payment_include_draft_move%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Alexandre Fayolle

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.