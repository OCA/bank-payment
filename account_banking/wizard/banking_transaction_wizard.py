# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 Therp BV (<http://therp.nl>).
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
from osv import osv, fields

"""

The banking transaction wizard is linked to a button in the statement line
tree view. It allows the user to undo the duplicate flag, select between
multiple matches or select a manual match.

"""

class banking_transaction_wizard(osv.osv_memory):
    _name = 'banking.transaction.wizard'
    _description = 'Match transaction'

    def create_act_window(self, cr, uid, ids, nodestroy=True, context=None):
        """ 
        Return a popup window for this model
        """
        if isinstance(ids, (int, float)):
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

    def trigger_match(self, cr, uid, ids, context=None):
        """
        Call the automatic matching routine for one or
        more bank transactions
        """
        if isinstance(ids, (int, float)):
            ids = [ids]
        import_transaction_obj = self.pool.get('banking.import.transaction')
        trans_id = self.read(
            cr, uid, ids[0], ['import_transaction_id'],
            context=context)['import_transaction_id'][0] # many2one tuple
        import_transaction_obj.match(cr, uid, [trans_id], context=context)
        return True
    
    def write(self, cr, uid, ids, vals, context=None):
        """
        Implement a trigger to retrieve the corresponding move line
        when the invoice_id changes
        """
        res = super(banking_transaction_wizard, self).write(
            cr, uid, ids, vals, context=context)
        if vals and 'invoice_id' in vals:
            statement_line_obj = self.pool.get('account.bank.statement.line')
            transaction_obj = self.pool.get('banking.import.transaction')
            for wiz in self.browse(cr, uid, ids, context=context):
                if (wiz.import_transaction_id.match_type == 'invoice' and
                    wiz.import_transaction_id.invoice_id):
                    # the current value might apply
                    if (wiz.move_line_id and wiz.move_line_id.invoice and
                        wiz.move_line_id.invoice.id == wiz.invoice_id.id):
                        found = True
                        continue
                    # Otherwise, retrieve the move line for this invoice
                    # Given the arity of the relation, there is are always
                    # multiple possibilities but the move lines here are
                    # prefiltered for having account_id.type payable/receivable
                    # and the regular invoice workflow should only come up with 
                    # one of those only.
                    for move_line in wiz.import_transaction_id.move_line_ids:
                        if (move_line.invoice.id ==
                            wiz.import_transaction_id.invoice_id.id):
                            transaction_obj.write(
                                cr, uid, wiz.import_transaction_id.id,
                                { 'move_line_id': move_line.id, }, context=context)
                            statement_line_obj.write(
                                cr, uid, wiz.import_transaction_id.statement_line_id.id,
                                { 'partner_id': move_line.invoice.partner_id.id,
                                  'account_id': move_line.account_id.id,
                                  }, context=context)
                            found = True
                            break
                    # Cannot match the invoice 
                    if not found:
                        # transaction_obj.write(
                        #   cr, uid, wiz.import_transaction_id.id,
                        #   { 'invoice_id': False, }, context=context)
                        osv.except_osv(
                            _("No entry found for the selected invoice"),
                            _("No entry found for the selected invoice. " +
                              "Try manual reconciliation."))

    def select_match(self, cr, uid, ids, context=None):
        """
        Just a button that triggers a write.
        """
        return True

    def reverse_duplicate(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, float)):
            ids = [ids]
        transaction_obj = self.pool.get('banking.import.transaction')
        for wiz in self.read(cr, uid, ids, ['duplicate', 'import_transaction_id'], context=context):
            transaction_obj.write(
                cr, uid, wiz['import_transaction_id'][0], 
                {'duplicate': not wiz['duplicate']}, context=context)
        return True

    def _get_default_match_type(self, cr, uid, context=None):
        """
        Take initial value for the match type from the statement line
        """
        res = False
        if context and 'statement_line_id' in context:
            res = self.pool.get('account.bank.statement.line').read(
                cr, uid, context['statement_line_id'],
                ['match_type'], context=context)['match_type']
        return res

    def button_done(self, cr, uid, ids, context=None):
        return {'nodestroy': False, 'type': 'ir.actions.act_window_close'}        

    _defaults = {
        'match_type': _get_default_match_type,
        }

    _columns = {
        'name': fields.char('Name', size=64),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line', 'Statement line',
            ),
        'amount': fields.related(
            'statement_line_id', 'amount', type='float',
            string="Amount", readonly=True),
        'import_transaction_id': fields.related(
            'statement_line_id', 'import_transaction_id', 
            string="Import transaction",
            type='many2one', relation='banking.import.transaction'),
        'residual': fields.related(
            'import_transaction_id', 'residual', type='float', 
            string='Residual'),
        'payment_line_id': fields.related(
            'import_transaction_id', 'payment_line_id', string="Matching payment or storno", 
            type='many2one', relation='payment.line'),
        'payment_order_ids': fields.related(
            'import_transaction_id', 'payment_order_ids', string="Matching payment orders", 
            type='many2many', relation='payment.order'),
        'payment_order_id': fields.related(
            'import_transaction_id', 'payment_order_id', string="Payment order to reconcile", 
            type='many2one', relation='payment.order'),
        'invoice_ids': fields.related(
            'import_transaction_id', 'invoice_ids', string="Matching invoices", 
            type='many2many', relation='account.invoice'),
        'invoice_id': fields.related(
            'import_transaction_id', 'invoice_id', string="Invoice to reconcile", 
            type='many2one', relation='account.invoice'),
        'move_line_ids': fields.related(
            'import_transaction_id', 'move_line_ids', string="Move lines",
            type='many2many', relation='account.move.line'),
        'move_line_id': fields.related(
            'import_transaction_id', 'move_line_id', string="Move lines",
            type='many2one', relation='account.move.line'),
        'duplicate': fields.related(
            'import_transaction_id', 'duplicate', string='Flagged as duplicate',
            type='boolean'),
        'match_multi': fields.related(
            'import_transaction_id', 'match_multi', 
            type="boolean", string='Multiple matches'),
        'match_type': fields.selection(
            [('manual', 'Manual'), ('move','Move'), ('invoice', 'Invoice'),
             ('payment', 'Payment'), ('payment_order', 'Payment order'),
             ('storno', 'Storno')], 'Match type', readonly=True),
        'manual_invoice_id': fields.many2one(
            'account.invoice', 'Match this invoice',
            domain=[('state', '=', 'open')]),
        'manual_payment_order_id': fields.many2one(
            'payment.order', "Payment order to reconcile"),
        'manual_move_line_id': fields.many2one(
            'account.move.line', 'Match this entry',
            domain=[('reconcile_id', '=', False),
                    ('account_id.reconcile', '=', True)]
            ),
        }
banking_transaction_wizard()

