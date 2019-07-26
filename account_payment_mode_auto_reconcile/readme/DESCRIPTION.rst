This module adds a checkbox `auto_reconcile_outstanding_credits` on account
payment modes to allow automatic reconciliation on account invoices if it is
checked.

Automatic reconciliation of outstanding credits will only happen on customer
invoices at validation if the payment mode is set or when the payment mode is
changed on an open invoice. If a payment mode using auto-reconcile is removed
from an open invoice, the existing auto reconciled payments will be removed.

Another option `auto_reconcile_allow_partial` on account payment mode defines
if outstanding credits can be partially used for the auto reconciliation.
