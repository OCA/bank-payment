.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

============================
Account Payment Order Return
============================

This module adds a check in the wizard where move lines are imported into
payment order.
This check lets include in selection lines from invoices linked to a
payment return.

Installation
============

This module is auto-installed when you install *account_payment_return* and
*account_payment_order*.

Usage
=====

#. Go to Invoicing > Payments > Debit Orders.
#. Create a new record.
#. Click on button "Create Payment Lines fron Journal Items" to open the
   wizard.
#. Click on the "Include move lines from returns " check.
#. Fill other options.
#. Click on button "Add All Move Lines".

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Luis M. Ontalba <luis.martinez@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
