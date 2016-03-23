# -*- coding: utf-8 -*-
# © 2014 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_mode_id = fields.Many2one(
        comodel_name='payment.mode', string="Payment Mode",
        domain="[('type', '=', type)]")

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if type == 'in_invoice':
                res['value']['payment_mode_id'] = \
                    partner.supplier_payment_mode.id
            elif type == 'out_invoice':
                res['value']['payment_mode_id'] = \
                    partner.customer_payment_mode.id
                # Do not change the default value of partner_bank_id if
                # partner.customer_payment_mode is False
                if partner.customer_payment_mode.bank_id:
                    res['value']['partner_bank_id'] = \
                        partner.customer_payment_mode.bank_id.id
        else:
            res['value']['payment_mode_id'] = False
        return res
