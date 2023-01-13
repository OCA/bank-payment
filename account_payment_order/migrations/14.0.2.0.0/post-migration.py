# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _insert_account_payments(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_payment ADD old_bank_payment_line_id INT4"
    )
    # Create an account.payment record for each bank.payment.line
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment (
            create_date, create_uid, write_date, write_uid, old_bank_payment_line_name,
            payment_order_id, partner_id, amount, currency_id,
            payment_method_id, old_bank_payment_line_id, payment_type,
            partner_type,
            destination_account_id, payment_reference, move_id
        )
        SELECT
            bpl.create_date, bpl.create_uid, bpl.write_date, bpl.write_uid, bpl.name,
            bpl.order_id, bpl.partner_id, bpl.amount_currency, 1,
            apm.payment_method_id, bpl.id, apo.payment_type,
            CASE WHEN apo.payment_type = 'inbound' THEN 'customer' ELSE 'supplier' END,
            aml.account_id, bpl.communication, aml.move_id
        FROM bank_payment_line bpl
        JOIN account_payment_order apo ON apo.id = bpl.order_id
        JOIN account_payment_mode apm ON apm.id = apo.payment_mode_id
        LEFT JOIN account_move_line aml ON aml.bank_payment_line_id = bpl.id
        WHERE apo.state not in ('uploaded', 'done') or aml.move_id is not null
        """,
    )
    # As the information is asymmetric: N payment lines > 1 bank payment line, but there
    # are some related non-stored fields to payment lines, we need a second query to
    # update some of the fields
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET currency_id = apl.currency_id,
            partner_bank_id = apl.partner_bank_id
        FROM account_payment_line apl
        WHERE apl.bank_line_id = ap.old_bank_payment_line_id
        """,
    )


def _create_hooks(env):
    """Avoid errors due to locked dates, overriding involved methods."""

    def _check_fiscalyear_lock_date(self):
        return True

    def _check_tax_lock_date(self):
        return True

    def _check_reconciliation(self):
        return True

    # create hooks
    _check_fiscalyear_lock_date._original_method = type(
        env["account.move"]
    )._check_fiscalyear_lock_date
    type(env["account.move"])._check_fiscalyear_lock_date = _check_fiscalyear_lock_date
    _check_tax_lock_date._original_method = type(
        env["account.move.line"]
    )._check_tax_lock_date
    type(env["account.move.line"])._check_tax_lock_date = _check_tax_lock_date
    _check_reconciliation._original_method = type(
        env["account.move.line"]
    )._check_reconciliation
    type(env["account.move.line"])._check_reconciliation = _check_reconciliation


def create_moves_from_orphan_account_payments(env):
    """Recreate missing journal entries on the newly created account payments."""
    env.cr.execute(
        """
        SELECT ap.id, MIN(apl.date), MIN(bpl.company_id), MIN(apo.name),
            MIN(apo.journal_id), MIN(apl.currency_id), MIN(apo.state), MIN(apo.id)
        FROM bank_payment_line bpl
        JOIN account_payment ap ON ap.old_bank_payment_line_id = bpl.id
        JOIN account_payment_order apo ON apo.id = bpl.order_id
        JOIN account_payment_line apl ON apl.bank_line_id = bpl.id
        LEFT JOIN account_move_line aml ON aml.bank_payment_line_id = bpl.id
        WHERE aml.move_id IS NULL
        GROUP BY ap.id
        """
    )
    deprecated_acc_by_company = {}
    for row in env.cr.fetchall():
        payment = (
            env["account.payment"]
            .with_context(
                check_move_validity=False,
                tracking_disable=True,
            )
            .browse(row[0])
        )
        move = env["account.move"].create(
            {
                "name": "/",
                "date": row[1],
                "payment_id": payment.id,
                "move_type": "entry",
                "company_id": row[2],
                "ref": row[3],
                "journal_id": row[4],
                "currency_id": row[5],
                "state": "draft" if row[6] in {"open", "generated"} else "cancel",
                "payment_order_id": row[7],
            }
        )
        payment.move_id = move
        # Avoid deprecated account warning
        if payment.company_id not in deprecated_acc_by_company:
            deprecated_accounts = env["account.account"].search(
                [("deprecated", "=", True), ("company_id", "=", payment.company_id.id)]
            )
            deprecated_acc_by_company[payment.company_id] = deprecated_accounts
            deprecated_accounts.deprecated = False
        try:
            payment._synchronize_to_moves(["date"])  # no more changed fields needed
        except Exception as e:
            _logger.error("Failed for payment with id %s: %s", payment.id, e)
            raise
    # Restore deprecated accounts
    for deprecated_accounts in deprecated_acc_by_company.values():
        deprecated_accounts.deprecated = True


def _delete_hooks(env):
    """Restore the locking dates original methods."""
    type(env["account.move"])._check_fiscalyear_lock_date = type(
        env["account.move"]
    )._check_fiscalyear_lock_date._original_method
    type(env["account.move.line"])._check_tax_lock_date = type(
        env["account.move.line"]
    )._check_tax_lock_date._original_method
    type(env["account.move.line"])._check_reconciliation = type(
        env["account.move.line"]
    )._check_reconciliation._original_method


def _insert_payment_line_payment_link(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_account_payment_line_rel
        (account_payment_id, account_payment_line_id)
        SELECT ap.id, apl.id
        FROM account_payment_line apl
        JOIN account_payment ap ON ap.old_bank_payment_line_id = apl.bank_line_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_payment ALTER move_id DROP NOT NULL"
    )
    _insert_account_payments(env)
    _create_hooks(env)
    create_moves_from_orphan_account_payments(env)
    openupgrade.logged_query(
        env.cr, "ALTER TABLE account_payment ALTER move_id SET NOT NULL"
    )
    _delete_hooks(env)
    _insert_payment_line_payment_link(env)
