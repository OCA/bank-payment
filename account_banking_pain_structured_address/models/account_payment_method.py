# Copyright 2026 Vignesh Babu S
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    sepa_pain09_address_mode = fields.Selection(
        selection_add=[("structured", "Structured (street name and number)")],
        # On uninstall, fall back to Hybrid: like Structured, it keeps the street
        # and the postcode in the file (Minimal would drop them)
        ondelete={
            "structured": lambda methods: methods.write(
                {"sepa_pain09_address_mode": "hybrid"}
            )
        },
    )
