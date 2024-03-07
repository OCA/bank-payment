Module to export payment orders in SEPA XML file format.

SEPA PAIN (PAyment INitiation) is the new european standard for
Customer-to-Bank payment instructions. This module implements SEPA
Credit Transfer (SCT), more specifically PAIN versions 001.001.02,
001.001.03, 001.001.04 and 001.001.05. It is part of the ISO 20022
standard, available on <https://www.iso20022.org>.

The Implementation Guidelines for SEPA Credit Transfer published by the
European Payments Council (<https://www.europeanpaymentscouncil.eu>) use
PAIN version 001.001.03, so it's probably the version of PAIN that you
should try first.

It also includes pain.001.003.03 which is used in Germany instead of
001.001.03. You can read more about this here (only in german language):
<http://www.ebics.de/startseite/>
