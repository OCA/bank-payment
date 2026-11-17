.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

====================================
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

* Create a Payment Mode dedicated to SEPA Credit Transfer.

* Select the Payment Method *SEPA Credit Transfer to suppliers* (which is
  automatically created upon module installation).

* Check that this payment method uses the proper version of PAIN.

** PAIN.001.001.09 address handling **

When using format **pain.001.001.09**, the address block is no longer generated
using the legacy unstructured format, as this is invalid according to the
official schema.

You must configure the field “PAIN.001.001.09 Address Mode” on the payment
method:

- **Minimal (City + Country)**
  Generates only the mandatory structured elements `TwnNm` and `Ctry`.

- **Hybrid (City/Country + AdrLine)**
  Generates `TwnNm` and `Ctry`, plus optional `AdrLine` elements for street data.

If no address mode is selected, the default is **Minimal**, which is fully
schema-compliant.

Older PAIN formats (`pain.001.001.03`, `.04`, `.05`, etc.) are unaffected.

Usage
=====

In the menu *Accounting > Payments > Payment Order*, create a new
payment order and select the Payment Mode dedicated to SEPA Credit
Transfer that you created during the configuration step.

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


Authors
~~~~~~~

* Akretion
* Tecnativa
* Therp BV

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>
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

  * Axel Priem <axel.priem@dynapps.be>
* `Sygel Technology <https://www.sygel.es>`_:

  * Valentin Vinagre <valentin.vinagre@sygel.es>
* `Therp BV <https://www.therp.nl>`_:
  * Nikos Tsirintanis <ntsirintanis@therp.nl>

