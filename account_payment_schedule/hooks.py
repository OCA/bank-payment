# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Fill the scheduled date in SQL instead of computing it on every journal item."""
    cr.execute(
        """
        ALTER TABLE account_move_line
        ADD COLUMN IF NOT EXISTS payment_schedule_date date
        """
    )
    cr.execute(
        """
        UPDATE account_move_line aml
        SET payment_schedule_date = aml.date_maturity
        FROM account_account account
        WHERE account.id = aml.account_id
            AND account.account_type IN ('asset_receivable', 'liability_payable')
        """
    )
