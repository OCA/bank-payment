# -*- coding: utf-8 -*-
# Copyright 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # v8 fields : same without the _id suffix
    supplier_payment_mode_id = fields.Many2one(
        'account.payment.mode', string='Supplier Payment Mode',
        company_dependent=True,
        domain=[('payment_type', '=', 'outbound')],
        help="Select the default payment mode for this supplier.")
    customer_payment_mode_id = fields.Many2one(
        'account.payment.mode', string='Customer Payment Mode',
        company_dependent=True,
        domain=[('payment_type', '=', 'inbound')],
        help="Select the default payment mode for this customer.")

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res += ['supplier_payment_mode_id', 'customer_payment_mode_id']
        return res
