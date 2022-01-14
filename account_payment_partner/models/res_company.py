# Copyright 2022 - CampToCamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    force_blank_partner_bank_id = fields.Boolean(
        string="Force blank partner bank",
        default=True,
        help="No bank account assignation is done for out_invoice as this is only"
        " needed for printing purposes and it can conflict with"
        " SEPA direct debit payments. Current report prints it.",
    )
