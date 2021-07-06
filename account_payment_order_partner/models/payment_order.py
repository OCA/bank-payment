# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    partner_id = fields.Many2one("res.partner", string="Partner")
    state = fields.Selection(selection_add=[("new", "New")])
