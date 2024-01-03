import logging

from odoo.tools import sql

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Prepare new partner_bank_id computed field.

    Add column to avoid MemoryError on an existing Odoo instance
    with lots of data.

    partner_bank_id on account.move.line requires payment_order_ok to be True
    which it won't be as it's newly introduced - nothing to compute.
    (see AccountMoveLine._compute_partner_bank_id() in models/account_move_line.py
    and AccountMove._compute_payment_order_ok() in models/account_move.py)
    """
    if not sql.column_exists(env.cr, "account_move_line", "partner_bank_id"):
        sql.create_column(env.cr, "account_move_line", "partner_bank_id", "int4")
