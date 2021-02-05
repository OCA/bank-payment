# © 2013-2014 ACSONE SA (<https://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_order_ok = fields.Boolean(
        compute="_compute_payment_order_ok",
    )
    # we restore this field from <=v11 for now for preserving behavior
    # TODO: Check if we can remove it and base everything in something at
    # payment mode or company level
    reference_type = fields.Selection(
        selection=[
            ('none', 'Free Reference'),
            ('structured', 'Structured Reference'),
        ],
        string='Payment Reference',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='none',
    )

    @api.depends('payment_mode_id', 'move_id', 'move_id.line_ids',
                 'move_id.line_ids.payment_mode_id')
    def _compute_payment_order_ok(self):
        for invoice in self:
            payment_mode = (
                invoice.move_id.line_ids.filtered(
                    lambda x: not x.reconciled
                ).mapped('payment_mode_id')[:1]
            )
            if not payment_mode:
                payment_mode = invoice.payment_mode_id
            invoice.payment_order_ok = payment_mode.payment_order_ok

    @api.model
    def line_get_convert(self, line, part):
        """Copy supplier bank account from invoice to account move line"""
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('type') == 'dest' and line.get('invoice_id'):
            invoice = self.browse(line['invoice_id'])
            if invoice.type in ('in_invoice', 'in_refund'):
                res['partner_bank_id'] = invoice.partner_bank_id.id or False
        return res

    @api.multi
    def create_account_payment_line(self):
        for inv in self:
            if inv.state != 'open':
                raise UserError(_(
                    "The invoice %s is not in Open state") % inv.number)
            if not inv.move_id:
                raise UserError(_(
                    "No Journal Entry on invoice %s") % inv.number)

        return self.mapped("move_id.line_ids").filtered(
            lambda x: x.account_id.internal_type in (
                'receivable', 'payable')).action_add_to_payment_order()

    @api.multi
    def action_invoice_cancel(self):
        self.mapped("move_id.line_ids").filtered(
            'payment_line_ids').action_cancel_payment_line()
        return super().action_invoice_cancel()

