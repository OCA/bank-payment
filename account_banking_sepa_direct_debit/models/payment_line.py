# -*- encoding: utf-8 -*-
##############################################################################
#
#    SEPA Direct Debit module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    sdd_mandate_id = fields.Many2one(
        'sdd.mandate', string='SEPA Direct Debit Mandate',
        domain=[('state', '=', 'valid')])

    def create(self, vals=None):
        """If the customer invoice has a mandate, take it. Otherwise, take the
        first valid mandate of the bank account.
        """
        if not vals:
            vals = {}
        partner_bank_id = vals.get('bank_id')
        if (self.env.context.get('search_payment_order_type') == 'debit'
                and 'sdd_mandate_id' not in vals):
            if vals.get('move_line_id'):
                line = self.env['account.move.line'].browse(
                    vals['move_line_id'])
                if (line.invoice and line.invoice.type == 'out_invoice'
                        and line.invoice.sdd_mandate_id):
                    vals.update(
                        {'sdd_mandate_id': line.invoice.sdd_mandate_id.id,
                         'bank_id':
                         line.invoice.sdd_mandate_id.partner_bank_id.id})
            if partner_bank_id and 'sdd_mandate_id' not in vals:
                mandates = self.env['sdd.mandate'].search(
                    [('partner_bank_id', '=', partner_bank_id),
                     ('state', '=', 'valid')])
                if mandates:
                    vals['sdd_mandate_id'] = mandates.ids[0]
        return super(PaymentLine, self).create(vals)

    @api.one
    @api.constrains('sdd_mandate_id', 'bank_id')
    def _check_mandate_bank_link(self):
        if (self.sdd_mandate_id and self.bank_id
                and self.sdd_mandate_id.partner_bank_id.id !=
                self.bank_id.id):
            raise exceptions.Warning(
                _('Error:'),
                _("The payment line with reference '%s' has the bank "
                    "account '%s' which is not attached to the mandate "
                    "'%s' (this mandate is attached to the bank account "
                    "'%s').") %
                (self.name,
                 self.bank_id.name_get()[0][1],
                 self.sdd_mandate_id.unique_mandate_reference,
                 self.sdd_mandate_id.partner_bank_id.name_get()[0][1]))
