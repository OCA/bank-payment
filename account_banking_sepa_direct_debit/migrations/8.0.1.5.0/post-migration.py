# coding: utf-8
# © 2016 Opener B.V. - Stefan Rijnhart
import logging
from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    """ Create amendment triggers on mandates that have a different bank
    account than their last payment line """
    logger = logging.getLogger(__name__)
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        cr.execute(
            """
            WITH latest_line AS (
                SELECT abm.partner_bank_id, (
                    SELECT pl.id AS plid FROM payment_line pl
                        JOIN payment_order po ON pl.order_id = po.id
                    WHERE pl.mandate_id = abm.id
                        AND po.date_sent IS NOT NULL
                        OR po.date_done IS NOT NULL
                    ORDER BY COALESCE(po.date_sent, po.date_done) DESC
                    LIMIT 1)
                 FROM account_banking_mandate abm
                 WHERE state = 'valid' AND type = 'recurrent')
            SELECT mandate_id, pl.bank_id AS line_bank FROM latest_line
                JOIN payment_line pl ON pl.id = plid
            WHERE partner_bank_id != pl.bank_id;
            """)
        for row in cr.fetchall():
            mandate = env['account.banking.mandate'].browse(row[0])
            old_bank = env['res.partner.bank'].browse(row[1])
            mandate.write(env['account.banking.mandate'].get_amendment_vals(
                old_bank, mandate.partner_bank_id))
            logger.info(
                'Setting amendment trigger for mandate %s (previously for '
                'account %s)', mandate.unique_mandate_reference,
                old_bank.acc_number)
