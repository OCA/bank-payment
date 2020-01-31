This modules adds one field on sale orders: *Payment Mode*.
This field is copied from customer to sale order and then from sale order to
customer invoice.

This module is similar to the *sale_payment* module; the main difference is
that it doesn't depend on the *account_payment_extension* module (it's not the
only module to conflict with *account_payment_extension*; all the SEPA
modules in the banking addons conflict with *account_payment_extension*.
