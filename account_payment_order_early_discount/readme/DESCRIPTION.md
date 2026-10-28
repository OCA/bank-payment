This module targets the **native early payment discount of Odoo 18** (payment terms with
_Early Discount_, discount percentage and discount days). Without it,
`account_payment_order` (SEPA credit transfer and others) is not usable for vendor bills
with such payment terms:

- the _Create Transactions_ wizard only selects bills by their net due date, i.e. after
  the discount period has ended;
- the payment line always takes the full amount, the discount is never deducted;
- a manually reduced amount leaves the bill partially open, because the payment entry of
  the order does not book the discount (unlike the _Register Payment_ wizard).

This module makes payment orders behave like _Register Payment_ for these payment terms:

- the _Create Transactions_ wizard can also select bills whose discount must be paid up
  to the filter date, not only bills that are due by then;
- payment lines get the **discounted amount** and, if the payment mode pays on the
  discount date, the **discount date** as execution date (moved to a working day); this
  amount and date go into the payment file;
- when the order is confirmed, the lines follow the current open amount of the bill
  (e.g. a credit note reconciled in the meantime) and the discount is checked again
  against the actual execution date (full amount and a chatter note if the discount
  period is over; manually changed amounts are kept);
- when the order is uploaded, the payment entry books the discount and the tax
  correction exactly like the _Register Payment_ wizard, so the bill is fully
  reconciled.

Credit notes and partial settlements, which Odoo does not handle for early payment
discounts (no discount once a bill is partially reconciled, credit notes deducted in
full):

- open discount = discount of the bill minus the discount of what is already settled: a
  credit note showing a discount takes away its own discount, one without discount
  nothing, a partial payment the proportional discount;
- a credit note in the same payment is deducted with its discounted amount only; its
  discount is booked back on the discount account with the tax correction.

Direct debit orders handle customer invoices with an early discount the same way: an
amount collected within the discount period is collected with the discount, as the
customer would get it with _Register Payment_. Collecting on the net due date (option
_Pay Early Discounts on Discount Date_ disabled) collects the full amount.
