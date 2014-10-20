# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Partner module for OpenERP
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
        'payment_mode_id': fields.many2one(
            'payment.mode', 'Payment Mode'),
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
            if type == 'in_invoice':
                res['value']['payment_mode_id'] = \
                    partner.supplier_payment_mode.id or False
            elif type == 'out_invoice':
                res['value'].update({
                    'payment_mode_id':
                    partner.customer_payment_mode.id or False,
                    'partner_bank_id':
                    partner.customer_payment_mode and
                    partner.customer_payment_mode.bank_id.id or False,
                })
        else:
            res['value']['payment_mode_id'] = False
        return res
