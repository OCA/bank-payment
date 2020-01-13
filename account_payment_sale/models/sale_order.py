# Copyright 2014-2016 Akretion - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_mode_id = fields.Many2one(
        'account.payment.mode', string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')])

    def _get_payment_mode_vals(self, vals):
        if self.payment_mode_id:
            vals['payment_mode_id'] = self.payment_mode_id.id
            if (self.payment_mode_id.bank_account_link == 'fixed' and
                    self.payment_mode_id.payment_method_id.code == 'manual'):
                vals['partner_bank_id'] =\
                    self.payment_mode_id.fixed_journal_id.bank_account_id.id
        return vals

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self.payment_mode_id = self.partner_id.with_context(
                force_company=self.company_id.id
            ).customer_payment_mode_id
        else:
            self.payment_mode_id = False
        return res

    @api.multi
    def _prepare_invoice(self):
        """Copy bank partner from sale order to invoice"""
        vals = super()._prepare_invoice()
        return self._get_payment_mode_vals(vals)

    def _finalize_invoices(self, invoices, references):
        """
        Invoked after creating invoices at the end of action_invoice_create.

        We must override this method since the onchange on partner is called by
        the base method and therefore will change the specific payment_mode set
        on the SO if one is defined on the partner..

        :param invoices: {group_key: invoice}
        :param references: {invoice: order}
        """
        payment_vals_by_invoice = {}
        for invoice in invoices.values():
            payment_vals_by_invoice[invoice] = {
                'payment_mode_id': invoice.payment_mode_id.id,
                'partner_bank_id': invoice.partner_bank_id.id
            }
        res = super()._finalize_invoices(invoices, references)
        for invoice in invoices.values():
            payment_vals = payment_vals_by_invoice[invoice]
            if invoice.payment_mode_id.id == payment_vals['payment_mode_id']:
                payment_vals.pop("payment_mode_id")
            if invoice.partner_bank_id.id == payment_vals["partner_bank_id"]:
                payment_vals.pop("partner_bank_id")
            if payment_vals:
                invoice.write(payment_vals)
        return res
