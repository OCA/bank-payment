This module adds 2 fields on purchase orders: *Bank Account* and *Payment
Mode*. These fields are copied from partner to purchase order and then from
purchase order to supplier invoice.

This module is similar to the *purchase_payment* module; the main difference
is that it doesn't depend on the *account_payment_extension* module (it's not
the only module to conflict with *account_payment_extension*; all the SEPA
modules in the banking addons conflict with *account_payment_extension*).
