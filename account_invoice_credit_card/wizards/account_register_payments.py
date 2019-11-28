# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)\
            ._prepare_payment_vals(invoices)
        if self.payment_method_code == 'electronic':
            if invoices[0].partner_id.type == 'invoice':
                partner_id = invoices[0].partner_id
            else:
                partner_id = invoices[0].commercial_partner_id
            if partner_id.payment_token_id:
                res['payment_token_id'] = partner_id.payment_token_id.id
            else:
                raise UserError(
                    _('Invoice %s: Partner %s does not have'
                      ' a default payment method.')
                    % (res['communication'], partner_id.display_name)
                )
        return res

    def get_payments_vals(self):
        res = super(AccountRegisterPayments, self)\
            .get_payments_vals()
        if self.payment_method_code == 'electronic':
            token_ids = map(lambda x: x.get('payment_token_id'), res)
            tokens = self.env['payment.token'].browse(token_ids)
            acquirers = tokens.mapped('acquirer_id')
            if len(acquirers) > 1:
                raise UserError(
                    _("Electronic batch payments are limited"
                      " to a single provider. These were found: %s")
                    % (", ".join(acquirers.mapped('display_name')))
                )
        return res
