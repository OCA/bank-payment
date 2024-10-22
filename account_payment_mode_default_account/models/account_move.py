# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from contextlib import contextmanager

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _get_payment_term_lines(self):
        self.ensure_one()
        return self.line_ids.filtered(
            lambda line: line.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )

    def _change_account_on_lines(self):
        self.ensure_one()
        payment_term_lines = self._get_payment_term_lines()
        payment_mode_id = self.payment_mode_id.id
        partner = self.partner_id.with_context(
            _partner_property_account_payment_mode=payment_mode_id
        )
        if self.is_sale_document(include_receipts=True):
            payment_term_lines.account_id = partner.property_account_receivable_id
        else:
            payment_term_lines.account_id = partner.property_account_payable_id

    @contextmanager
    def _sync_dynamic_line(
        self,
        existing_key_fname,
        needed_vals_fname,
        needed_dirty_fname,
        line_type,
        container,
    ):
        with super()._sync_dynamic_line(
            existing_key_fname,
            needed_vals_fname,
            needed_dirty_fname,
            line_type,
            container,
        ):
            yield
        if line_type == "payment_term":
            invoices = container.get("records")
            invoices = invoices.filtered(lambda invoice: invoice.state == "draft")
            for inv in invoices:
                inv._change_account_on_lines()

    @api.onchange("payment_mode_id")
    def _onchange_payment_mode_id(self):
        if self.payment_mode_id and self.partner_id:
            if self.state == "draft":
                self._change_account_on_lines()
