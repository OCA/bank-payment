# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def update_bank_journals(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ajo = env['account.journal']
        journals = ajo.search([('type', '=', 'bank')])
        sct_id = env['ir.model.data'].xmlid_to_res_id(
            'account_banking_sepa_credit_transfer.sepa_credit_transfer')
        if sct_id:
            journals.write({
                'outbound_payment_method_ids': [(4, sct_id)],
            })
    return
