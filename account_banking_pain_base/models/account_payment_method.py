# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    pain_version = fields.Selection([], string="PAIN Version", copy=False)
    convert_to_ascii = fields.Boolean(
        string='Convert to ASCII', default=True,
        help="If active, Odoo will convert each accented character to "
        "the corresponding unaccented character, so that only ASCII "
        "characters are used in the generated PAIN file.")
    pain_bank_address = fields.Boolean(
        string='Bank Address in PAIN XML',
        help="If enabled, the name and address of the bank will be set "
        "in the appropriate XML tags (if the bank account is linked to a "
        "bank and if the information is set on the related bank). "
        "Some banks reject PAIN XML files that contain the name and "
        "address of the bank, although the ISO 20022 "
        "standard and the EPC guidelines specify this possibility.")
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

    @api.multi
    def get_xsd_file_path(self):
        """This method is designed to be inherited in the SEPA modules"""
        self.ensure_one()
        raise UserError(_(
            "No XSD file path found for payment method '%s'") % self.name)

    _sql_constraints = [(
        # Extending this constraint from account_payment_mode
        'code_payment_type_unique',
        'unique(code, payment_type, pain_version)',
        'A payment method of the same type already exists with this code'
        ' and PAIN version'
    )]
