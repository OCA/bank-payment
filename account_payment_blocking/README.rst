.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Block payment of invoices
=========================

This module was written to extend the functionality of payment orders
to prevent invoices under litigation to be presented for inclusion in payment orders.

This module uses the 'blocked' flag that is present on journal items
to filter out lines proposed in payment orders.

In addition it exposes this flag on the supplier invoice form
so it is easier to block an invoice.

Installation
============

This module depends on account_banking_payment_export that is part 
of the OCA/bank-payment suite.

Configuration
=============

There is nothing to configure.

Usage
=====

To use this module, set the "Blocked" flag on supplier invoices
or on payable/receivable journal items.

These invoices will not be proposed for inclusion in payment orders.

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

None.

Credits
=======

Contributors
------------

* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

