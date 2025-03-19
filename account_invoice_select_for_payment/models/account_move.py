# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    selected_for_payment = fields.Boolean(
        string="To Pay",
        compute="_compute_selected_for_payment",
        readonly=False,
        store=True,
        tracking=True,
    )

    def action_toggle_select_for_payment(self):
        selected = self.filtered(lambda rec: rec.selected_for_payment)
        unselected = self - selected
        if selected:
            selected.write({"selected_for_payment": False})
        if unselected:
            unselected.write({"selected_for_payment": True})

    @api.depends("payment_state")
    def _compute_selected_for_payment(self):
        for rec in self:
            if rec.payment_state in ("in_payment", "paid", "reversed"):
                rec.selected_for_payment = False

    def action_register_payment(self):
        invoices = self.filtered(lambda inv: inv.selected_for_payment)
        if invoices:
            invoices.write({"selected_for_payment": False})
        return super().action_register_payment()
