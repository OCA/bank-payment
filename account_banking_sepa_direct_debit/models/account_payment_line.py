# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def draft2open_payment_line_check(self):
        res = super().draft2open_payment_line_check()
        sepa_dd_lines = self.filtered(
            lambda line: line.order_id.payment_method_id.code == "sepa_direct_debit"
        )
        sepa_dd_lines._check_sepa_direct_debit_ready()
        return res

    def _check_sepa_direct_debit_ready(self):
        """
        This method checks whether the payment line(s) are ready to be used
        in the SEPA Direct Debit file generation.
        :raise: UserError if a line does not fulfils all requirements
        """
        for rec in self:
            if not rec.mandate_id:
                raise UserError(
                    _(
                        "Missing SEPA Direct Debit mandate on the line with "
                        "partner {partner_name} (reference {reference})."
                    ).format(partner_name=rec.partner_id.name, reference=rec.name)
                )
            if rec.mandate_id.state != "valid":
                raise UserError(
                    _(
                        "The SEPA Direct Debit mandate with reference "
                        "{mandate_ref} for partner {partner_name} has "
                        "expired."
                    ).format(
                        mandate_ref=rec.mandate_id.unique_mandate_reference,
                        partner_name=rec.partner_id.name,
                    )
                )
            if rec.mandate_id.type == "oneoff" and rec.mandate_id.last_debit_date:
                raise UserError(
                    _(
                        "The SEPA Direct Debit mandate with reference "
                        "{mandate_ref} for partner {partner_name} has type set "
                        "to 'One-Off' but has a last debit date set to "
                        "{last_debit_date}. Therefore, it cannot be used."
                    ).format(
                        mandate_ref=rec.mandate_id.unique_mandate_reference,
                        partner_name=rec.partner_id.name,
                        last_debit_date=rec.mandate_id.last_debit_date,
                    )
                )
