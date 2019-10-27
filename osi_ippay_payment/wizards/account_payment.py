# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
