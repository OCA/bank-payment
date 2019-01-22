.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=======================================
Account Payment Clearing Systems Module
=======================================

This module allows to set a 'Clearing System Member Identification' type on a bank (res.bank) and
provide a Clearing System Member Identification Number which is needed for banks that don't have a
Bank Identifier Code (BIC) to generate a PAIN (payment instruction) file that can be used for international
payments.

The module was built using the specifications listed here: https://www.iso20022.org/external_code_list.page

Installation
============

This module depends on:

- account_banking_pain_base

This module is part of the OCA/bank-payment suite.

Configuration
=============

#. Go to Sales > Configuration > Banks.
#. For all the banks that don't have a Bank Identifier Code (BIC) set the appropriate
   Clearing System Member Identification (CSMI) and the country.
#. Set a Clearing System Member Identification Number that is valid for the chosen CSMI.

(Now if you generate a PAIN file from a payment order with a payment to one of those banks
the payment instruction will have the appropriate target information.)

Usage
=====

See 'readme' files of the OCA/bank-payment suite.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/10.0

Known issues / Roadmap
======================

 * Unfortunately at this point in time in Germany it is not possible to make a payment to a
bank account without an IBAN using a PAIN file (this is due to the PAIN variant that they use).

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

* Timka Piric Muratovic (brain-tec AG)
* Tobias Bächle (brain-tec AG)

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
