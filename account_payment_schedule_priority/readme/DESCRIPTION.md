When cash is short, this module decides who gets paid first in the payment
schedule of `account_payment_schedule`.

Each journal item gets a payment priority: Critical, High, Normal or Low. It comes
from the partner and can be changed on the item in the schedule, one at a time or
several at once. The schedule can be filtered and grouped by priority.

*Replan by Priority*, on top of the cash flow chart, looks at the dates of the
next 30 days whose projected balance is below the minimum balance. On each of
them, the lowest priority items, latest due date first, move to the first date
from which the projected balance stays at or above the minimum, until the date is
no longer short. Critical items and items of confirmed payment orders keep their
date. A preview lists the items to move, the items kept because no later date has
enough balance, and the dates that stay short; nothing changes before it is
applied.
