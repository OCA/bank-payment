# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'

    include_returned = fields.Boolean(
        string='Include move lines from returns')

    @api.multi
    def _prepare_move_line_domain(self):
        domain = super(AccountPaymentLineCreate,
                       self)._prepare_move_line_domain()
        if not self.include_returned:
            domain.append(('invoice_id.returned_payment', '=', False))
        return domain
