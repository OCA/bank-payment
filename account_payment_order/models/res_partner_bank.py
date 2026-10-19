# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.constrains("bank_bic")
    def check_bic_length(self):
        for bank in self:
            if bank.bank_bic and len(bank.bank_bic) not in (8, 11):
                raise ValidationError(
                    self.env._(
                        "A valid BIC contains 8 or 11 characters. The BIC '%(bic)s' "
                        "contains %(num)d characters, so it is not valid.",
                        bic=bank.bank_bic,
                        num=len(bank.bank_bic),
                    )
                )
