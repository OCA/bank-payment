import logging

from odoo.tools import sql

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Prepare new payment_mode fields.

    Add columns to avoid Memory error on an existing Odoo instance
    with lots of data.

    The payment_mode_id fields are introduced by this module and computed only
    from each other or the also newly introduced supplier_payment_mode_id and
    customer_payment_mode_id on res.partner, so they can stay NULL, nothing
    to compute.
    """
    if not sql.column_exists(cr, "account_move", "payment_mode_id"):
        sql.create_column(cr, "account_move", "payment_mode_id", "int4")
    if not sql.column_exists(cr, "account_move_line", "payment_mode_id"):
        sql.create_column(cr, "account_move_line", "payment_mode_id", "int4")
