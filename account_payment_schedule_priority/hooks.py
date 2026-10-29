# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Create the priority column with its default instead of computing it on
    every journal item: no partner has a priority before the install."""
    cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN IF NOT EXISTS payment_priority varchar DEFAULT '3'
        """
    )
    cr.execute(
        "ALTER TABLE account_move_line ALTER COLUMN payment_priority DROP DEFAULT"
    )
