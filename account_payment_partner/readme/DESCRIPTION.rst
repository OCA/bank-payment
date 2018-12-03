This module adds severals fields:

* the *Supplier Payment Mode* and *Customer Payment Mode* on Partners,

* the *Payment Mode* on Invoices.

* the *Show bank account* on Payment Mode.

* the *# of digits for customer bank account* on Payment Mode.

* the *Bank account from journals* on Payment Mode.

On a Payment Order, in the wizard *Select Invoices to Pay*, the invoices will
be filtered per Payment Mode.

Allows to print in the invoice to which account number the payment
(via SEPA direct debit) is going to be charged so the customer knows that
information, but there are some customers that don't want that everyone
looking at the invoice sees the full account number (and even GDPR can say a
word about that), so that's the reason behind the several options.
