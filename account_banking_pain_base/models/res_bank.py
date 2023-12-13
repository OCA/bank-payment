# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, models
from odoo.exceptions import ValidationError

BIC_REGEX = re.compile(r"[A-Z]{6}[A-Z2-9][A-NP-Z0-9]([A-Z0-9]{3})?$")


class ResBank(models.Model):
    _inherit = "res.bank"

    @api.constrains("bic")
    def _check_bic(self):
        """
        This method strengthens the constraint on the BIC of the bank account
        (The account_payment_order module already checks the length in the
         check_bic_length method).
        :raise: ValidationError if the BIC doesn't respect the regex of the
        SEPA pain schemas.
        """
        invalid_banks = self.filtered(lambda r: r.bic and not BIC_REGEX.match(r.bic))
        if invalid_banks:
            raise ValidationError(
                _(
                    "The following Bank Identifier Codes (BIC) do not respect "
                    "the SEPA pattern:\n{bic_list}\n\nSEPA pattern: "
                    "{sepa_pattern}"
                ).format(
                    sepa_pattern=BIC_REGEX.pattern,
                    bic_list="\n".join(invalid_banks.mapped("bic")),
                )
            )
