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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class payment_line(orm.Model):
    _inherit = 'payment.line'

    _columns = {
        'mandate_id': fields.many2one(
            'account.banking.mandate', 'Direct Debit Mandate',
            domain=[('state', '=', 'valid')]),
    }

    def create(self, cr, uid, vals, context=None):
        ''' If the customer invoice has a mandate, take it
        otherwise, take the first valid mandate of the bank account
        '''
        if context is None:
            context = {}
        if not vals:
            vals = {}
        partner_bank_id = vals.get('bank_id')
        move_line_id = vals.get('move_line_id')
        if (context.get('search_payment_order_type') == 'debit' and
                'mandate_id' not in vals):
            if move_line_id:
                line = self.pool['account.move.line'].browse(
                    cr, uid, move_line_id, context=context)
                if (line.invoice and line.invoice.type == 'out_invoice' and
                        line.invoice.mandate_id):
                    vals.update({
                        'mandate_id': line.invoice.mandate_id.id,
                        'bank_id':
                        line.invoice.mandate_id.partner_bank_id.id,
                    })
            if partner_bank_id and 'mandate_id' not in vals:
                mandate_ids = self.pool['account.banking.mandate'].search(
                    cr, uid, [
                        ('partner_bank_id', '=', partner_bank_id),
                        ('state', '=', 'valid'),
                    ], context=context)
                if mandate_ids:
                    vals['mandate_id'] = mandate_ids[0]
        return super(payment_line, self).create(cr, uid, vals, context=context)

    def _check_mandate_bank_link(self, cr, uid, ids):
        for payline in self.browse(cr, uid, ids):
            if (payline.mandate_id and payline.bank_id and
                    payline.mandate_id.partner_bank_id.id !=
                    payline.bank_id.id):
                raise orm.except_orm(
                    _('Error:'),
                    _("The payment line with reference '%s' has the bank "
                        "account '%s' which is not attached to the mandate "
                        "'%s' (this mandate is attached to the bank account "
                        "'%s').") %
                    (payline.name,
                     self.pool['res.partner.bank'].name_get(
                         cr, uid, [payline.bank_id.id])[0][1],
                     payline.mandate_id.unique_mandate_reference,
                     self.pool['res.partner.bank'].name_get(
                         cr, uid,
                         [payline.mandate_id.partner_bank_id.id])[0][1],)
                )
        return True

    _constraints = [
        (_check_mandate_bank_link, 'Error msg in raise',
            ['mandate_id', 'bank_id']),
    ]
