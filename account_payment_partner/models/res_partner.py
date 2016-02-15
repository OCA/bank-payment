# -*- coding: utf-8 -*-
# © 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_payment_mode = fields.Many2one(
        'payment.mode', string='Supplier Payment Mode', company_dependent=True,
        domain="[('purchase_ok', '=', True)]",
        help="Select the default payment mode for this supplier.")
    customer_payment_mode = fields.Many2one(
        'payment.mode', string='Customer Payment Mode', company_dependent=True,
        domain="[('sale_ok', '=', True)]",
        help="Select the default payment mode for this customer.")

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res += ['supplier_payment_mode', 'customer_payment_mode']
        return res
