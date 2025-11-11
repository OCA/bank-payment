# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    pain_version = fields.Selection([], string="PAIN Version", copy=False)
    convert_to_ascii = fields.Boolean(
        string="Convert to ASCII",
        default=True,
        help="If active, Odoo will convert each accented character to "
        "the corresponding unaccented character, so that only ASCII "
        "characters are used in the generated PAIN file.",
    )
    warn_not_sepa = fields.Boolean(string="Warn If Not SEPA")
    # get rid of booleans, add selection
    sepa_pain09_address_mode = fields.Selection(
        [
            ("minimal", "Minimal (City + Country only)"),
            ("hybrid", "Hybrid (City/Country + AdrLine)"),
        ],
        default="minimal",
        required=True,
        string="PAIN.001.001.09 Address Mode",
        help=(
            "Controls how the <PstlAdr> block is generated for PAIN.001.001.09"
            "- Minimal: only City (TwnNm) and Country (Ctry)"
            "- Hybrid: City/Country plus optional AdrLine lines (street/street2) "
            "and optional Post Code (PstCd) when available."
        ),
    )

    def get_xsd_file_path(self):
        """This method is designed to be inherited in the SEPA modules"""
        self.ensure_one()
        raise UserError(
            self.env._("No XSD file path found for payment method '%s'", self.name)
        )

    _code_payment_type_unique = models.Constraint(
        "unique(code, payment_type, pain_version)",
        "A payment method of the same type already exists with this code"
        " and PAIN version",
    )
