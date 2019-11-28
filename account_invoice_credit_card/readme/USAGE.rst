This module allows to add partner credit card.

* On the Partner form, or in an Invoice, click on the "Add Credit Card" button, and fill in the credit card details.
* On the Partner form, the "Credit Card(s)" smart button gives access to the Saved Payment Data, with the stored credit card tokens.


Pay an Invoice using a stored Credit Card:

* On an open invoice, select the "Payment" button and choose the Journal configured for IPPay.
* Then select the "Electronic" option and the pick the saved Credit Card token from the list of available ones.

Pay multiple invoices using stored Credit Card tokens:

* On the invoice list, selecte the Invoices to pay. They must be open, and share the same payment processor.
* On the Action menu select the "Register Payments" option.

In Batch Payment using a credit card, a payment confirmation will done through cron job named 'Post process payment transactions'.
