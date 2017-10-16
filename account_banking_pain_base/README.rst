.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

================================
Account Banking PAIN Base Module
================================

This module contains fields and functions that are used by the module for SEPA
Credit Transfer (account_banking_sepa_credit_transfer) and SEPA Direct Debit
(account_banking_sepa_direct_debit). This module doesn't provide any
functionality by itself.

This module was started during the Akretion-Noviat code sprint of November
21st 2013 in Epiais les Louvres (France).

Installation
============

This module depends on :

- account_payment_order

This module is part of the OCA/bank-payment suite.

Configuration
=============

#. Go to Invoicing/Accounting > Configuration > Settings.
#. On the fields "Initiating Party Issuer" and "Initiating Party Identifier",
   in the section *SEPA/PAIN*, you can fill the corresponding identifiers.

If your country requires several identifiers (like Spain), you must:

#. Go to *Invoicing/Accounting > Configuration > Settings*.
#. On the section *SEPA/PAIN*, check the mark "Multiple identifiers".
#. Now go to *Invoicing/Accounting > Configuration > Management > Payment Modes*.
#. Create a payment mode for your specific bank.
#. Fill the specific identifiers on the fields "Initiating Party Identifier"
   and "Initiating Party Issuer".

Usage
=====

See 'readme' files of the OCA/bank-payment suite.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/11.0

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
* Pedro M. Baeza
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Ignacio Ibeas - Acysos S.L.
* Alexandre Fayolle
* Raphaël Valyi
* Sandy Carter
* Stefan Rijnhart (Therp)
* Antonio Espinosa <antonioea@antiun.com>

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
