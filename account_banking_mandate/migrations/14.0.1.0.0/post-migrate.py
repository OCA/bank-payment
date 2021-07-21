# Copyright 2021 Opener B.V. - Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo.tools.sql import column_exists


def migrate(cr, version):
    logger = logging.getLogger(
        "odoo.addons.account_banking_mandate.migrations.14.0.1.0.0"
    )
    if not column_exists(cr, "account_move_line", "mandate_id"):
        logger.warning(
            "Column account_move_line.mandate_id not found when "
            "populating account_move.mandate_id"
        )
        return
    logger.info(
        "Populating account_move.mandate_id from obsolete "
        "account_move_line.mandate_id"
    )
    cr.execute(
        """
        UPDATE account_move am
        SET mandate_id = aml.mandate_id
        FROM account_move_line aml
        WHERE aml.mandate_id IS NOT NULL
            AND am.mandate_id IS NULL
            AND am.id=aml.move_id
        """
    )
