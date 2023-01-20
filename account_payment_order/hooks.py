from odoo.tools import sql


def pre_init_hook(cr):
    """Prepare new computed fields.

    Add columns to avoid MemoryError on an existing Odoo instance
    with lots of data.

    payment_order_ok on account.move is computed from payment_order_ok
    on account.payment.mode which are both introduced by this module,
    so nothing to compute.
    (see AccountMove._compute_payment_order_ok() in models/account_move.py)

    partner_bank_id on account.move.line requires payment_order_ok to be True
    which it won't be as it's newly introduced - again nothing to compute.
    (see AccountMoveLine._compute_partner_bank_id() in models/account_move_line.py)
    """
    if not sql.column_exists(cr, "account_move", "payment_order_ok"):
        sql.create_column(cr, "account_move", "payment_order_ok", "bool")

    if not sql.column_exists(cr, "account_move_line", "partner_bank_id"):
        sql.create_column(cr, "account_move_line", "partner_bank_id", "int4")
