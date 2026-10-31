Glue between ``account_payment_schedule`` and ``account_payment_order_api``,
installed automatically with both.

* An item whose payment is refused, rejected, cancelled or returned by the bank
  comes back to the payment schedule right away, even while the rest of its
  order is still at the bank.
* The schedule shows the status and the reason given by the bank to the last
  payment of each item.
* Three counters on top of the schedule: awaiting release at the bank, refused
  by the bank (items back in the schedule) and outcome unknown.
