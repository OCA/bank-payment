# -*- encoding: utf-8 -*-
##############################################################################
#
#    Mandate module for openERP
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    @author: Cyril Sester <csester@compassion.ch>,
#             Alexis de Lattre <alexis.delattre@akretion.com>
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

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')])

    @api.model
    def create(self, vals=None):
        """If the customer invoice has a mandate, take it
        otherwise, take the first valid mandate of the bank account
        """
        if vals is None:
            vals = {}
        partner_bank_id = vals.get('bank_id')
        move_line_id = vals.get('move_line_id')
        if (self.env.context.get('search_payment_order_type') == 'debit' and
                'mandate_id' not in vals):
            if move_line_id:
                line = self.env['account.move.line'].browse(move_line_id)
                if (line.invoice and line.invoice.type == 'out_invoice' and
                        line.invoice.mandate_id):
                    vals.update({
                        'mandate_id': line.invoice.mandate_id.id,
                        'bank_id': line.invoice.mandate_id.partner_bank_id.id,
                    })
            if partner_bank_id and 'mandate_id' not in vals:
                mandates = self.env['account.banking.mandate'].search(
                    [('partner_bank_id', '=', partner_bank_id),
                     ('state', '=', 'valid')])
                if mandates:
                    vals['mandate_id'] = mandates[0].id
        return super(PaymentLine, self).create(vals)

    @api.one
    @api.constrains('mandate_id', 'bank_id')
    def _check_mandate_bank_link(self):
        if (self.mandate_id and self.bank_id and
                self.mandate_id.partner_bank_id.id !=
                self.bank_id.id):
            raise exceptions.Warning(
                _("The payment line with reference '%s' has the bank account "
                  "'%s' which is not attached to the mandate '%s' (this "
                  "mandate is attached to the bank account '%s').") %
                (self.name,
                 self.bank_id.name_get()[0][1],
                 self.mandate_id.unique_mandate_reference,
                 self.mandate_id.partner_bank_id.name_get()[0][1]))
