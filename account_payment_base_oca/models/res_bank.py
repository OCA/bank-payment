# Copyright 2015-2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, models
from odoo.exceptions import ValidationError

BIC_REGEX = re.compile(r"[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?$")


class ResBank(models.Model):
    _inherit = "res.bank"

    @api.constrains("bic")
    def _check_bic_length(self):
        for bank in self:
            if bank.bic:
                if len(bank.bic) not in (8, 11):
                    raise ValidationError(
                        _(
                            "A valid BIC contains 8 or 11 characters. BIC '%(bic)s' "
                            "contains %(num)d characters, so it is not valid.",
                            bic=bank.bic,
                            num=len(bank.bic),
                        )
                    )
                if not BIC_REGEX.match(bank.bic):
                    raise ValidationError(
                        _(
                            "BIC '%(bic)s' doesn't respect the standard "
                            "pattern '{pattern}'.",
                            bic=bank.bic,
                            pattern=BIC_REGEX.pattern,
                        )
                    )
