# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.account_banking.wizard import banktools

class link_partner(orm.TransientModel):
    _name = 'banking.link_partner'
    _inherit = 'res.partner.address'
    _description = 'Link partner'

    _columns = {
        'name': fields.char(
            'Create partner with name', size=128, required=True),
        'supplier': fields.boolean('Supplier'),
        'customer': fields.boolean('Customer'),
        'partner_id': fields.many2one(
            'res.partner', 'or link existing partner'),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line',
            'Statement line', required=True),
        'remote_account': fields.char(
            'Account number', size=24, readonly=True),
        }
    
    def create(self, cr, uid, vals, context=None):
        """
        Get default values from the transaction data 
        on the statement line
        """
        if vals and vals.get('statement_line_id'):
            statement_line_obj = self.pool.get('account.bank.statement.line')
            statement_line = statement_line_obj.browse(
                cr, uid, vals['statement_line_id'], context=context)
            transaction = statement_line.import_transaction_id

            if statement_line.partner_bank_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Statement line is already linked to a bank account '))
            
            if not(transaction and transaction.remote_owner
                   and transaction.remote_account):
                raise orm.except_orm(
                    _('Error'),
                    _('No transaction data on statement line'))

            if 'supplier' not in vals and statement_line.amount < 0:
                vals['supplier'] = True
            if 'customer' not in vals and statement_line.amount > 0:
                vals['customer'] = True

            if not vals.get('street'):
                vals['street'] = transaction.remote_owner_address
            if not vals.get('street'):
                vals['city'] = transaction.remote_owner_city
            if not vals.get('country_id'):
                vals['country_id'] = banktools.get_country_id(
                    self.pool, cr, uid, transaction, context=context)
            if not vals.get('name'):
                vals['name'] = transaction.remote_owner
            if not vals.get('remote_account'):
                vals['remote_account'] = transaction.remote_account

        return super(link_partner, self).create(
            cr, uid, vals, context=context)
            
    def link_partner(self, cr, uid, ids, context=None):
        statement_line_obj = self.pool.get(
            'account.bank.statement.line')
        wiz = self.browse(cr, uid, ids[0], context=context)

        if wiz.partner_id:
            partner_id = wiz.partner_id.id
        else:
            partner_id = self.pool.get('res.partner').create(
                cr, uid, {
                    'name': wiz.name,
                    'customer': wiz.customer,
                    'supplier': wiz.supplier, 
                    }, context=context)
            wiz_read = self.read(
                cr, uid, ids[0], context=context, load='_classic_write')
            address_fields = self.pool.get(
                'res.partner.address')._columns.keys()
            for field in self._columns.keys():
                # NB: wizard model contains 'partner_id' like the address
                # but in this code path it is False
                if field in address_fields:
                    address_vals[field] = wiz_read[field]
            address_vals.update({
                    'partner_id': partner_id,
                    'type': 'default',
                    })
            self.pool.get('res.partner.address').create(
                cr, uid, address_vals, context=context)
            
        partner_bank_id = banktools.create_bank_account(
            self.pool, cr, uid, partner_id,
            wiz.remote_account, wiz.name,
            wiz.street, wiz.city,
            wiz.country_id and wiz.country_id.id or False,
            bic=wiz.statement_line_id.import_transaction_id.remote_bank_bic
            )

        statement_line_ids = statement_line_obj.search(
            cr, uid,
            [('import_transaction_id.remote_account', '=', wiz.remote_account),
             ('partner_bank_id', '=', False),
             ('state', '=', 'draft')], context=context)
        statement_line_obj.write(
            cr, uid, statement_line_ids,
            {'partner_bank_id': partner_bank_id,
             'partner_id': partner_id}, context=context)

        return {'type': 'ir.actions.act_window_close'}        

    def create_act_window(self, cr, uid, ids, nodestroy=True, context=None):
        """ 
        Return a popup window for this model
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        return {
            'name': self._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
            'nodestroy': nodestroy,
            }


