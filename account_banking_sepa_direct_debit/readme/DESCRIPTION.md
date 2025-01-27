Module to export direct debit orders in SEPA XML file format.

[ISO 20022](https://www.iso20022.org/) is the new international standard
for bank XML files. This module implements SEPA Direct Debit (SDD), more
specifically ISO 20022 PAIN (PAyment INitiation) versions 008.001.02 and
008.001.08. It follows the [SEPA direct debit implementation
guidelines](https://www.europeanpaymentscouncil.eu/what-we-do/sepa-direct-debit)
of the [European Payments
Council](https://www.europeanpaymentscouncil.eu).

This module also supports PAIN version 008.003.02 which is used in
Germany. You can read more about this in german on
[ebics.de](https://www.ebics.de/).

It supports both SEPA **Core** and SEPA **B2B** mandates.
