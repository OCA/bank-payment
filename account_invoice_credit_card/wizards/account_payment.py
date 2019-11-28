# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_token_id = fields.Many2one('payment.token',
                                       string="Saved payment token",
                                       help="Note that tokens from acquirers\
                                        set to only authorize transactions\
                                         (instead of capturing the amount)\
                                          are not available.")

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments,
                    self)._prepare_payment_vals(invoices)
        res.update({'payment_token_id': self.payment_token_id.id})
        return res

    @api.onchange('partner_id', 'payment_method_id', 'journal_id')
    def _onchange_set_payment_token_id(self):
        res = {}

        if not self.payment_method_code == 'electronic' or not self.partner_id or not self.journal_id:
            self.payment_token_id = False
            return res

        partners = self.partner_id | self.partner_id.commercial_partner_id | self.partner_id.commercial_partner_id.child_ids
        domain = [('partner_id', 'in', partners.ids),
                  ('acquirer_id.journal_id', '=', self.journal_id.id)]
        if self.partner_id.payment_token_id:
            self.payment_token_id = self.partner_id.payment_token_id.id
        else:
            self.payment_token_id = self.env['payment.token'].search(domain,
                                                                     limit=1)

        res['domain'] = {'payment_token_id': domain}
        return res
