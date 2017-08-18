.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=================================
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

* account_banking_pain_base
* account_banking_mandate

This module is part of the OCA/bank-payment suite.

Configuration
=============

For setting the SEPA creditor identifier:

#. Go to Accounting > Configuration > Settings.
#. On the field "SEPA Creditor Identifier" in the section *SEPA/PAIN*, you can
   fill the corresponding identifier.

If your country requires several identifiers (like Spain), you must:

#. Go to *Accounting > Configuration > Settings*.
#. On the section *SEPA/PAIN*, check the mark "Multiple identifiers".
#. Now go to *Accounting > Configuration > Management > Payment Modes*.
#. Create a payment mode for your specific bank.
#. Fill the specific identifier on the field "SEPA Creditor Identifier".

For defining a payment mode that uses SEPA direct debit:

#. Go to *Accounting > Configuration > Management > Payment Modes*.
#. Create a record.
#. Select the Payment Method *SEPA Direct Debit for customers* (which is
   automatically created upon module installation).
#. Check that this payment method uses the proper version of PAIN.
#. If not, go *Accounting > Configuration > Management > Payment Methods*.
#. Locate the "SEPA Direct Debit for customers" record and open it.
#. Change the "PAIN version" according your needs.
#. If you need to handle several PAIN versions, just duplicate the payment
   method adjusting this field on each for having them.

Usage
=====

In the menu *Accounting > Payments > Debit Order*, create a new debit
order and select the Payment Mode dedicated to SEPA Direct Debit that
you created during the configuration step.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/10.0

Known issues / Roadmap
======================

 * No known issues

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
* Alexandre Fayolle
* Raphaël Valyi
* Sandy Carter
* Antonio Espinosa <antonioea@antiun.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
