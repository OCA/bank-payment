# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _default_outbound_payment_methods(self):
        all_out = self.env['account.payment.method'].search([
            ('payment_type', '=', 'outbound')])
        return all_out

    def _default_inbound_payment_methods(self):
        all_in = self.env['account.payment.method'].search([
            ('payment_type', '=', 'inbound')])
        return all_in

    outbound_payment_method_ids = fields.Many2many(
        default=_default_outbound_payment_methods)
    inbound_payment_method_ids = fields.Many2many(
        default=_default_inbound_payment_methods)
    company_partner_id = fields.Many2one(
        'res.partner', related='company_id.partner_id',
        readonly=True)  # Used in domain of field bank_account_id
