from openupgradelib import openupgrade


def _init_values(cr):
    query = """
        UPDATE payment_transaction
            SET persistent_state_message = state_message
    """
    openupgrade.logged_query(cr, query)


def post_init_hook(cr, registry):
    _init_values(cr)
