# Copyright 2016-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    code = fields.Char(
        string="Code (Do Not Modify)",
        help="This code is used in the code of the Odoo module that handles "
        "this payment method. Therefore, if you change it, "
        "the generation of the payment file may fail.",
    )
    active = fields.Boolean(default=True)
    bank_account_required = fields.Boolean(
        help="Activate this option if this payment method requires you to "
        "know the bank account number of your customer or supplier."
    )
    payment_mode_ids = fields.One2many(
        comodel_name="account.payment.mode",
        inverse_name="payment_method_id",
        string="Payment modes",
    )

    @api.depends("code", "name", "payment_type")
    def name_get(self):
        result = []
        for method in self:
            result.append(
                (
                    method.id,
                    "[{}] {} ({})".format(
                        method.code, method.name, method.payment_type
                    ),
                )
            )
        return result

    def write(self, vals):
        res = super().write(vals)
        methods_info = self._get_payment_method_information().keys()
        if (
            "code" in vals
            and vals.get("code", False)
            and vals.get("code") not in methods_info
        ):
            raise UserError(
                _(
                    "You cann't use '{}' code for payment method."
                    " if you change it, the generation of the payment file may fail."
                    " \nPlease use '{}' codes."
                ).format(vals.get("code"), ", ".join(list(methods_info)))
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        methods_info = self._get_payment_method_information().keys()
        for vals in vals_list:
            if vals and vals.get("code", False) not in methods_info:
                raise UserError(
                    _(
                        "You cann't use '{}' code for payment method."
                        " if you change it, the generation of the payment file may fail."
                        " \nPlease use '{}' codes."
                    ).format(vals.get("code"), ", ".join(list(methods_info)))
                )
        return super().create(vals_list)
