# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import SUPERUSER_ID


def update_bank_journals(cr, pool):
    ajo = pool['account.journal']
    journal_ids = ajo.search(
        cr, SUPERUSER_ID, [('type', '=', 'bank')])
    sct_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID,
        'account_banking_sepa_credit_transfer.sepa_credit_transfer')
    if sct_id:
        ajo.write(cr, SUPERUSER_ID, journal_ids, {
            'outbound_payment_method_ids': [(4, sct_id)],
        })
    return
