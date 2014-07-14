[![Build Status](https://travis-ci.org/OCA/banking.svg?branch=7.0)](https://travis-ci.org/OCA/banking)
[![Coverage Status](https://img.shields.io/coveralls/OCA/banking.svg)](https://coveralls.io/r/OCA/banking?branch=7.0)

Banking addons for Odoo
=======================

This project focuses on in- and export of banking communication. The indentation below indicates
the dependency graph of the main modules.

- account_banking_payment_export - Basic export functionality of payment orders

    - account_banking_sepa_credit_transfer - Export of payment orders in SEPA format

    - account_direct_debit - Debit order infrastructure analogous to Odoo native payment orders

        - account_banking_sepa_direct_debit - Export of debit orders in SEPA format

- account_banking - Infrastructure for importing bank statements in various formats and custom (manual)
reconciliation functionality. While advanced, this functionality will be deprecated in Odoo 8.0 in favour
of (an extension of) the new, native reconciliation functionality.

    - account_banking_camt - Import of bank statements in the SEPA CAMT.053 format

A number of other modules are available for legacy format bank statement files.

Contact us
----------
Join the team on https://launchpad.net/~banking-addons-drivers so that you can subscribe to its mailing list
