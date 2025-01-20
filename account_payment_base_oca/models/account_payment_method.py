# Copyright 2016-2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    # native field, we just inherit string and help
    code = fields.Char(
        string="Code (do not modify)",
        help="This code is used in the source code of the Odoo module that handles "
        "this payment method. Therefore, if you change it, "
        "the generation of the payment file may fail.",
    )
    active = fields.Boolean(default=True)
    bank_account_required = fields.Boolean(
        help="Activate this option if this payment method requires you to "
        "know the bank account number of your customer or supplier."
    )
    # add the one2many field which is not native
    line_ids = fields.One2many(
        comodel_name="account.payment.method.line",
        inverse_name="payment_method_id",
        string="Payment Methods",
    )

    @api.depends("code", "name", "payment_type")
    def _compute_display_name(self):
        for method in self:
            name = f"[{method.code}] {method.name} ({method.payment_type})"
            method.display_name = name
