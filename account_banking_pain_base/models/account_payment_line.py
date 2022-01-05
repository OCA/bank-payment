# Copyright 2013-2022 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2014-2022 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2021-2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    priority = fields.Selection(
        [("NORM", "Normal"), ("HIGH", "High")],
        default="NORM",
        help="This field will be used as 'Instruction Priority' in "
        "the generated PAIN file.",
    )
    # local_instrument is used for instant credit transfers which
    # will begin on November 2017, cf account_banking_sepa_credit_transfer
    # It is also used in some countries such as switzerland,
    # cf l10n_ch_pain_base that adds some entries in the selection field
    local_instrument = fields.Selection([])
    category_purpose_id = fields.Many2one(
        "iso20022.code.list",
        domain=[("field", "=", "category_purpose")],
        ondelete="restrict",
        help="If neither your bank nor your local regulations oblige you to "
        "set the category purpose, leave the field empty.",
    )
    purpose_id = fields.Many2one(
        "iso20022.code.list",
        domain=[("field", "=", "purpose")],
        ondelete="restrict",
        help="If neither your bank nor your local regulations oblige you to "
        "set the category purpose, leave the field empty.",
    )
    # PAIN allows 140 characters
    communication = fields.Char(size=140)
    # The field struct_communication_type has been dropped in v9
    # We now use communication_type ; you should add an option
    # in communication_type with selection_add=[]
    communication_type = fields.Selection(
        selection_add=[("ISO", "ISO")], ondelete={"ISO": "cascade"}
    )
