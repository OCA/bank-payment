# Copyright 2016-2020 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    mandate_required = fields.Boolean(
        help="Activate this option if this payment method requires your "
        "customer to sign a direct debit mandate with your company.",
    )

    @api.constrains("mandate_required", "payment_type")
    def _check_mandate_required(self):
        for method in self:
            if method.payment_type != "inbound" and method.mandate_required:
                raise ValidationError(
                    _(
                        "The option 'Mandate Required' cannot be enabled on "
                        "payment method %s which is not an inbound payment method."
                    )
                    % method.display_name
                )
