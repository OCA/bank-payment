# Copyright 2017 Tecnativa - Luis M. Ontalba
# Copyright 2021 Tecnativa - João Marques
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    include_returned = fields.Boolean(string="Include move lines from returns")

    def _prepare_move_line_domain(self):
        domain = super()._prepare_move_line_domain()
        if not self.include_returned:
            domain += [
                ("move_id.returned_payment", "=", False),
            ]
        return domain
