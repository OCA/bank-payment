This module adds an option to generate extra grouped moves for the
payment orders since the refactoring done to use native Odoo payments.

This serves for easing the reconciliation on bank statements of large
payment orders, handling them as one or several journal entries
according payment date.

On large orders, the payments in each grouped move are reconciled in
batches instead of all at once, to avoid exhausting memory. The batch
size defaults to 1000 and can be changed with the
`account_payment_order_grouped_output.reconcile_batch_size` system
parameter.
