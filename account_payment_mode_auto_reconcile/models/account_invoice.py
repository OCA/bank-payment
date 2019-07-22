# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import json

from odoo import api, fields, models, _


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    # Allow changing payment mode in open state
    # TODO: Check if must be done in account_payment_partner instead
    payment_mode_id = fields.Many2one(
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}
    )
    payment_mode_warning = fields.Char(
        compute='_compute_payment_mode_warning',
    )
    display_payment_mode_warning = fields.Boolean(
        compute='_compute_payment_mode_warning',
    )

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            if invoice.type != 'out_invoice':
                continue
            if not invoice.payment_mode_id.auto_reconcile_outstanding_credits:
                continue
            partial_allowed = self.payment_mode_id.auto_reconcile_allow_partial
            invoice.auto_reconcile_credits(partial_allowed=partial_allowed)
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if 'payment_mode_id' in vals:
            for invoice in self:
                if invoice.state != 'open' or invoice.type != 'out_invoice':
                    continue
                payment_mode = invoice.payment_mode_id
                if (
                    payment_mode
                    and payment_mode.auto_reconcile_outstanding_credits
                ):
                    partial_allowed = payment_mode.auto_reconcile_allow_partial
                    invoice.auto_reconcile_credits(
                        partial_allowed=partial_allowed
                    )
                elif invoice.payment_move_line_ids:
                    invoice.auto_unreconcile_credits()
        return res

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

    @api.depends(
        'type', 'payment_mode_id', 'payment_move_line_ids', 'state',
        'has_outstanding'
    )
    def _compute_payment_mode_warning(self):
        # TODO Improve me but watch out
        for invoice in self:
            if invoice.type != 'out_invoice' or invoice.state == 'paid':
                invoice.payment_mode_warning = ''
                invoice.display_payment_mode_warning = False
                continue
            invoice.display_payment_mode_warning = True
            if (
                invoice.state != 'open' and invoice.payment_mode_id and
                invoice.payment_mode_id.auto_reconcile_outstanding_credits
            ):
                invoice.payment_mode_warning = _(
                    'Validating invoices with this payment mode will reconcile'
                    ' any outstanding credits.'
                )
                invoice.display_payment_mode_warning = True
            elif (
                invoice.state == 'open' and invoice.payment_move_line_ids and (
                    not invoice.payment_mode_id or not
                    invoice.payment_mode_id.auto_reconcile_outstanding_credits
                )
            ):
                invoice.payment_mode_warning = _(
                    'Changing payment mode will unreconcile existing payments.'
                )
                invoice.display_payment_mode_warning = True
            elif (
                invoice.state == 'open' and not invoice.payment_move_line_ids
                and invoice.payment_mode_id
                and invoice.payment_mode_id.auto_reconcile_outstanding_credits
                and invoice.has_outstanding
            ):
                invoice.payment_mode_warning = _(
                    'Changing payment mode will reconcile outstanding credits.'
                )
                invoice.display_payment_mode_warning = True
            else:
                invoice.payment_mode_warning = ''
                invoice.display_payment_mode_warning = False
