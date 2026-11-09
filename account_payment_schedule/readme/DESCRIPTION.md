This module adds a payment schedule: open vendor bills grouped by the date on
which they should be paid.

Each item gets a scheduled payment date, which starts as the due date, and an
instrument: the payment mode and, when the payment method needs one, the partner
bank account. Items that are ready are put in draft payment orders, one per
payment mode and date, with that fixed date. Confirming the order is the approval
to pay, so `account_payment_order_tier_validation` adds approval rules without
anything else.

No new document is created: the schedule is a view over the journal items and
their draft payment orders. An item that is in a draft, confirmed or generated
order cannot be scheduled again, the same rule as the wizard of the payment order.

On top of the schedule, a cash flow chart for the next 30 days shows the projected
balance per day: the balance of the bank and cash journals today, plus receivables
by due date, minus the scheduled payments. Overdue receivables are shown apart and
left out of the balance. The dates below the minimum balance of the company are
flagged, and the wizard and the draft payment order warn about them without
blocking.
