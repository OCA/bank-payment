# -*- coding: utf-8 -*-
# © 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def line_get_convert(self, line, part):
        """Copy mandate from invoice to account move line"""
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('type') == 'dest' and line.get('invoice_id'):
            invoice = self.browse(line['invoice_id'])
            if invoice.type in ('out_invoice', 'out_refund'):
                res['mandate_id'] = invoice.mandate_id.id or False
        return res

    # If a customer pays via direct debit, it's refunds should
    # be deducted form the next debit by default. The module
    # account_payment_partner copies payment_mode_id from invoice
    # to refund, and we also need to copy mandate from invoice to refund
    @api.model
    def _prepare_refund(
            self, invoice, date_invoice=None, date=None, description=None,
            journal_id=None):
        vals = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.type == 'out_invoice':
            vals['mandate_id'] = invoice.mandate_id.id
        return vals

    @api.onchange('payment_mode_id')
    def payment_mode_change(self):
        """Select by default the first valid mandate of the partner"""
        if (
                self.type in ('out_invoice', 'out_refund') and
                self.payment_mode_id.payment_type == 'inbound' and
                self.payment_mode_id.payment_method_id.mandate_required and
                self.partner_id):
            mandates = self.env['account.banking.mandate'].search([
                ('state', '=', 'valid'),
                ('partner_id', '=', self.commercial_partner_id.id),
                ])
            self.mandate_id = mandates[0]
