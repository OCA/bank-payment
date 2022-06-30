# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _recompute_payment_terms_lines(self):
        if self.payment_mode_id:
            return super(
                AccountMove,
                self.with_context(
                    _partner_property_account_payment_mode=self.payment_mode_id.id
                ),
            )._recompute_payment_terms_lines()
        else:
            return super()._recompute_payment_terms_lines()

    def _get_payment_term_lines(self):
        self.ensure_one()
        return self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        if self.payment_mode_id and self.partner_id:
            payment_term_lines = self._get_payment_term_lines()
            partner = self.partner_id.with_context(
                _partner_property_account_payment_mode=self.payment_mode_id.id
            )
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                payment_term_lines.account_id = partner.property_account_receivable_id
            else:
                payment_term_lines.account_id = partner.property_account_payable_id
