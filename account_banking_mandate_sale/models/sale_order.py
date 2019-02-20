# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # This field commercial_partner_id should be moved
    # in an OCA base module named for example sale_commercial_partner
    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id', string='Commercial Entity',
        store=True, readonly=True)
    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        ondelete='restrict', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    mandate_required = fields.Boolean(
        related='payment_mode_id.payment_method_id.mandate_required',
        readonly=True,
    )

    @api.multi
    def _prepare_invoice(self):
        """Copy mandate from sale order to invoice"""
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['mandate_id'] = self.mandate_id.id
        return vals

    @api.onchange('payment_mode_id')
    def payment_mode_change(self):
        """Select by default the first valid mandate of the partner"""
        self.ensure_one()
        if self.mandate_required and self.partner_id:
            mandates = self.env['account.banking.mandate'].search([
                ('state', '=', 'valid'),
                ('partner_id', '=', self.commercial_partner_id.id),
            ])
            self.mandate_id = mandates[:1]
        else:
            self.mandate_id = False
