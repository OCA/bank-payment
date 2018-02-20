# Copyright 2014 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        ondelete='restrict',
        readonly=True, states={'draft': [('readonly', False)]})
    mandate_required = fields.Boolean(
        related='payment_mode_id.payment_method_id.mandate_required',
        readonly=True)

    @api.model
    def line_get_convert(self, line, part):
        """Copy mandate from invoice to account move line"""
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('type') == 'dest' and line.get('invoice_id'):
            invoice = self.browse(line['invoice_id'])
            if invoice.type in ('out_invoice', 'out_refund'):
                res['mandate_id'] = invoice.mandate_id.id or False
        return res

    @api.model
    def create(self, vals):
        """Fill the mandate_id from the partner if none is provided on
        creation, using same method as upstream."""
        onchanges = {
            '_onchange_partner_id': ['mandate_id'],
            '_onchange_payment_mode_id': ['mandate_id'],
        }
        for onchange_method, changed_fields in list(onchanges.items()):
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(
                            invoice[field], invoice,
                        )
        return super(AccountInvoice, self).create(vals)

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

    def set_mandate(self):
        if self.payment_mode_id.payment_method_id.mandate_required:
            self.mandate_id = self.partner_id.valid_mandate_id
        else:
            self.mandate_id = False

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """Select by default the first valid mandate of the partner"""
        res = super(AccountInvoice, self)._onchange_partner_id()
        self.set_mandate()
        return res

    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        super(AccountInvoice, self)._onchange_payment_mode_id()
        self.set_mandate()

    @api.constrains('mandate_id', 'company_id')
    def _check_company_constrains(self):
        for inv in self:
            if inv.mandate_id.company_id and inv.mandate_id.company_id != \
                    inv.company_id:
                raise ValidationError(_(
                    "The invoice %s has a different company than "
                    "that of the linked mandate %s).") %
                    (inv.name, inv.mandate_id.display_name))
