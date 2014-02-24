# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Partner Payment module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'payment_mode_type': fields.many2one(
            'payment.mode.type', 'Payment Type'),
        }

    def onchange_partner_id(
            self, cr, uid, ids, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id)
            # TODO what about refunds ? Should be really copy
            # the payment type for refunds ?
            if type and type in ('in_invoice', 'in_refund'):
                res['value']['payment_mode_type'] = \
                    partner.supplier_payment_mode_type.id or False
            elif type and type in ('out_invoice', 'out_refund'):
                res['value']['payment_mode_type'] = \
                    partner.customer_payment_mode_type.id or False
        else:
            res['value']['payment_mode_type'] = False
        return res
