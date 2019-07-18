# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import json

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    # Allow changing payment mode in open state
    # TODO: Check if must be done in account_payment_partner instead
    payment_mode_id = fields.Many2one(
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
    )
    auto_assigned_oustanding_credits = fields.Boolean(
        compute='_compute_auto_assigned_oustanding_credits',
    )

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            if not invoice.payment_mode_id.auto_reconcile_outstanding_credits:
                continue
            partial_allowed = self.payment_mode_id.auto_reconcile_allow_partial
            invoice.auto_reconcile_credits(partial_allowed=partial_allowed)
        return res

    @api.onchange('payment_mode_id')
    def payment_mode_id_change(self):
        super(AccountInvoice, self).payment_mode_id_change()
        if self.state != 'open':
            return
        if (
            self.payment_mode_id
            and self.payment_mode_id.auto_reconcile_outstanding_credits
        ):
            partial_allowed = self.payment_mode_id.auto_reconcile_allow_partial
            self.auto_reconcile_credits(partial_allowed=partial_allowed)
        else:
            self.auto_unreconcile_credits()

    @api.multi
    def auto_reconcile_credits(self, partial_allowed=True):
        for invoice in self:
            if not invoice.has_outstanding:
                continue
            credits_info = json.loads(
                invoice.outstanding_credits_debits_widget
            )
            # Get outstanding credits in chronological order
            # (using reverse because aml is sorted by date desc as default)
            credits = credits_info.get('content')
            credits.reverse()
            for credit in credits:
                if (
                    not partial_allowed
                    and credit.get('amount') > invoice.residual
                ):
                    continue
                invoice.assign_outstanding_credit(credit.get('id'))

    @api.multi
    def auto_unreconcile_credits(self):
        for invoice in self:
            payments_info = json.loads(invoice.payments_widget or '{}')
            for payment in payments_info.get('content', []):
                aml = self.env['account.move.line'].browse(
                    payment.get('payment_id')
                )
                aml.with_context(invoice_id=invoice.id).remove_move_reconcile()

    @api.depends('payment_mode_id', 'payment_move_line_ids.amount_residual',
                 'state')
    def _compute_auto_assigned_oustanding_credits(self):
        for invoice in self:
            invoice.auto_assigned_oustanding_credits = (
                invoice.state == 'open' and
                invoice.payment_mode_id and
                invoice.payment_mode_id.auto_reconcile_outstanding_credits and
                invoice.payment_move_line_ids
            )
