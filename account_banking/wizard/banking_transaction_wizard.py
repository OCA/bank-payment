# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#              (C) 2011 Smile (<http://smile.fr>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import orm, fields
from openerp.tools.translate import _

"""

The banking transaction wizard is linked to a button in the statement line
tree view. It allows the user to undo the duplicate flag, select between
multiple matches or select a manual match.

"""


class banking_transaction_wizard(orm.TransientModel):
    _name = 'banking.transaction.wizard'
    _description = 'Match transaction'

    def create(self, cr, uid, vals, context=None):
        """
        Make sure that the statement line has an import transaction
        """
        res = super(banking_transaction_wizard, self).create(
            cr, uid, vals, context=context)
        if res and vals.get('statement_line_id'):
            line_pool = self.pool.get('account.bank.statement.line')
            line_pool.create_instant_transaction(
                cr, uid, vals['statement_line_id'], context=context)
        return res

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

    def trigger_match(self, cr, uid, ids, context=None):
        """
        Call the automatic matching routine for one or
        more bank transactions
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        import_transaction_obj = self.pool.get('banking.import.transaction')
        trans_id = self.read(
            cr, uid, ids[0], ['import_transaction_id'],
            context=context)['import_transaction_id'][0] # many2one tuple
        import_transaction_obj.match(cr, uid, [trans_id], context=context)
        return self.create_act_window(cr, uid, ids, context=None)
    
    def write(self, cr, uid, ids, vals, context=None):
        """
        Implement a trigger to retrieve the corresponding move line
        when the invoice_id changes
        """
        statement_line_obj = self.pool.get('account.bank.statement.line')
        transaction_obj = self.pool.get('banking.import.transaction')

        if not vals:
            return True

        # The following fields get never written
        # they are just triggers for manual matching
        # which populates regular fields on the transaction
        manual_invoice_id = vals.pop('manual_invoice_id', False)
        manual_move_line_id = vals.pop('manual_move_line_id', False)
        manual_invoice_ids = vals.pop('manual_invoice_ids', [])
        manual_move_line_ids = vals.pop('manual_move_line_ids', [])

        # Support for writing fields.related is still flakey:
        # https://bugs.launchpad.net/openobject-server/+bug/915975
        # Will do so myself.

        # Separate the related fields
        transaction_vals = {}
        wizard_vals = vals.copy()
        for key in vals.keys():
            field = self._columns[key]
            if (isinstance(field, fields.related) and
                field._arg[0] == 'import_transaction_id'):
                transaction_vals[field._arg[1]] = vals[key]
                del wizard_vals[key]

        # write the related fields on the transaction model
        if isinstance(ids, int):
            ids = [ids]
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.import_transaction_id:
                transaction_obj.write(
                    cr, uid, wizard.import_transaction_id.id,
                    transaction_vals, context=context)

        # write other fields to the wizard model
        res = super(banking_transaction_wizard, self).write(
            cr, uid, ids, wizard_vals, context=context)

        # End of workaround for lp:915975
        
        """ Process the logic of the written values """

        # An invoice is selected from multiple candidates
        if vals and 'invoice_id' in vals:
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
                        orm.except_orm(
                            _("No entry found for the selected invoice"),
                            _("No entry found for the selected invoice. " +
                              "Try manual reconciliation."))

        if manual_move_line_id or manual_invoice_id \
                or manual_move_line_ids or manual_invoice_ids:
            move_line_obj = self.pool.get('account.move.line')
            invoice_obj = self.pool.get('account.invoice')
            statement_line_obj = self.pool.get('account.bank.statement.line')
            manual_invoice_ids = (
                    ([manual_invoice_id] if manual_invoice_id else []) +
                    [i[1] for i in manual_invoice_ids if i[0]==4] +
                    [j for i in manual_invoice_ids if i[0]==6 for j in i[2]])
            manual_move_line_ids = (
                    ([manual_move_line_id] if manual_move_line_id else []) +
                    [i[1] for i in manual_move_line_ids if i[0]==4] +
                    [j for i in manual_move_line_ids if i[0]==6 for j in i[2]])
            for wiz in self.browse(cr, uid, ids, context=context):
                #write can be called multiple times for the same values
                #that doesn't hurt above, but it does here
                if wiz.match_type and (
                        len(manual_move_line_ids) > 1 or
                        len(manual_invoice_ids) > 1):
                    continue

                todo = []

                for invoice in invoice_obj.browse(
                        cr, uid, manual_invoice_ids, context=context):
                    found_move_line = False
                    if invoice.move_id:
                        for line in invoice.move_id.line_id:
                            if line.account_id.type in ('receivable', 'payable'):
                                todo.append((invoice.id, line.id))
                                found_move_line = True
                                break
                    if not found_move_line:
                        raise orm.except_orm(
                            _("Cannot select for reconcilion"),
                            _("No entry found for the selected invoice. "))
                for move_line_id in manual_move_line_ids:
                    todo_entry = [False, move_line_id]
                    move_line=move_line_obj.read(
                            cr,
                            uid,
                            move_line_id,
                            ['invoice'],
                            context=context)
                    if move_line['invoice']:
                        todo_entry[0] = move_line['invoice'][0]
                    todo.append(todo_entry)

                while todo:
                    todo_entry = todo.pop()
                    move_line = move_line_obj.browse(
                            cr, uid, todo_entry[1], context)
                    transaction_id = wiz.import_transaction_id.id
                    statement_line_id = wiz.statement_line_id.id

                    if len(todo) > 0:
                        statement_line_id = wiz.statement_line_id.split_off(
                                move_line.credit or move_line.debit)[0]
                        transaction_id = statement_line_obj.browse(
                                cr,
                                uid,
                                statement_line_id,
                                context=context).import_transaction_id.id

                    vals = {
                        'move_line_id': todo_entry[1],
                        'move_line_ids': [(6, 0, [todo_entry[1]])],
                        'invoice_id': todo_entry[0],
                        'invoice_ids': [(6, 0,
                            [todo_entry[0]] if todo_entry[0] else [])],
                        'match_type': 'manual',
                        }

                    transaction_obj.clear_and_write(
                        cr, uid, transaction_id, vals, context=context)

                    st_line_vals = {
                        'account_id': move_line_obj.read(
                            cr, uid, todo_entry[1], 
                            ['account_id'], context=context)['account_id'][0],
                        }

                    if todo_entry[0]:
                        st_line_vals['partner_id'] = invoice_obj.read(
                            cr, uid, todo_entry[0], 
                            ['partner_id'], context=context)['partner_id'][0]

                    statement_line_obj.write(
                        cr, uid, statement_line_id, 
                        st_line_vals, context=context)
        return res

    def trigger_write(self, cr, uid, ids, context=None):
        """
        Just a button that triggers a write.
        """
        return self.create_act_window(cr, uid, ids, context=None)

    def disable_match(self, cr, uid, ids, context=None):
        """
        Clear manual and automatic match information
        """
        settings_pool = self.pool.get('account.banking.account.settings')
        statement_pool = self.pool.get('account.bank.statement.line')

        if isinstance(ids, (int, long)):
            ids = [ids]

        for wiz in self.browse(cr, uid, ids, context=context):
            # Get the bank account setting record, to reset the account
            account_id = False
            journal_id = wiz.statement_line_id.statement_id.journal_id.id
            setting_ids = settings_pool.find(cr, uid, journal_id, context=context)
            if len(setting_ids)>0:
                setting = settings_pool.browse(cr, uid, setting_ids[0], context=context)
                if wiz.amount < 0:
                    account_id = setting.default_credit_account_id and setting.default_credit_account_id.id
                else:
                    account_id = setting.default_debit_account_id and setting.default_debit_account_id.id
                statement_pool.write(cr, uid, wiz.statement_line_id.id, {'account_id':account_id})
            
            wiz.write({'partner_id': False})

            if wiz.statement_line_id:
                #delete splits causing an unsplit if this is a split
                #transaction
                statement_pool.unlink(cr, uid,
                        statement_pool.search(cr, uid,
                            [('parent_id', '=', wiz.statement_line_id.id)],
                            context=context),
                        context=context)

            if wiz.import_transaction_id:
                wiz.import_transaction_id.clear_and_write()

        return self.create_act_window(cr, uid, ids, context=None)

    def reverse_duplicate(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        transaction_obj = self.pool.get('banking.import.transaction')
        for wiz in self.read(
            cr, uid, ids, ['duplicate', 'import_transaction_id'],
            context=context):
            transaction_obj.write(
                cr, uid, wiz['import_transaction_id'][0], 
                {'duplicate': not wiz['duplicate']}, context=context)
        return self.create_act_window(cr, uid, ids, context=None)

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
        return {'type': 'ir.actions.act_window_close'}        

    _defaults = {
#        'match_type': _get_default_match_type,
        }

    _columns = {
        'name': fields.char('Name', size=64),
        'statement_line_id': fields.many2one(
            'account.bank.statement.line', 'Statement line',
            ),
        'amount': fields.related(
            'statement_line_id', 'amount', type='float',
            string="Amount", readonly=True),
        'date': fields.related(
            'statement_line_id', 'date', type='date',
            string="Date", readonly=True),
        'ref': fields.related(
            'statement_line_id', 'ref', type='char', size=32,
            string="Reference", readonly=True),
        'partner_id': fields.related(
            'statement_line_id', 'partner_id',
            type='many2one', relation='res.partner',
            string="Partner", readonly=True),
        'statement_line_parent_id': fields.related(
            'statement_line_id', 'parent_id', type='many2one',
            relation='account.bank.statement.line', readonly=True),
        'import_transaction_id': fields.related(
            'statement_line_id', 'import_transaction_id', 
            string="Import transaction",
            type='many2one', relation='banking.import.transaction'),
        'residual': fields.related(
            'import_transaction_id', 'residual', type='float', 
            string='Residual', readonly=True),
        'writeoff_account_id': fields.related(
            'import_transaction_id', 'writeoff_account_id',
            type='many2one', relation='account.account',
            string='Write-off account'),
        'invoice_ids': fields.related(
            'import_transaction_id', 'invoice_ids', string="Matching invoices", 
            type='many2many', relation='account.invoice'),
        'invoice_id': fields.related(
            'import_transaction_id', 'invoice_id', string="Invoice to reconcile", 
            type='many2one', relation='account.invoice'),
        'move_line_ids': fields.related(
            'import_transaction_id', 'move_line_ids', string="Entry lines",
            type='many2many', relation='account.move.line'),
        'move_line_id': fields.related(
            'import_transaction_id', 'move_line_id', string="Entry line",
            type='many2one', relation='account.move.line'),
        'duplicate': fields.related(
            'import_transaction_id', 'duplicate', string='Flagged as duplicate',
            type='boolean'),
        'match_multi': fields.related(
            'import_transaction_id', 'match_multi', 
            type="boolean", string='Multiple matches'),
        'match_type': fields.related(
            'import_transaction_id', 'match_type', 
            type="char", size=16, string='Match type', readonly=True),
        'manual_invoice_id': fields.many2one(
            'account.invoice', 'Match this invoice',
            domain=[('reconciled', '=', False)]),
        'manual_move_line_id': fields.many2one(
            'account.move.line', 'Or match this entry',
            domain=[('account_id.reconcile', '=', True),
                    ('reconcile_id', '=', False)]),
        'manual_invoice_ids': fields.many2many(
            'account.invoice',
            'banking_transaction_wizard_account_invoice_rel',
            'wizard_id', 'invoice_id', string='Match following invoices',
            domain=[('reconciled', '=', False)]),
        'manual_move_line_ids': fields.many2many(
            'account.move.line',
            'banking_transaction_wizard_account_move_line_rel',
            'wizard_id', 'move_line_id',   string='Or match this entries',
            domain=[('account_id.reconcile', '=', True),
                    ('reconcile_id', '=', False)]),
        'payment_option': fields.related('import_transaction_id','payment_option', string='Payment Difference', type='selection', required=True,
                                         selection=[('without_writeoff', 'Keep Open'),('with_writeoff', 'Reconcile Payment Balance')]),
        'writeoff_analytic_id': fields.related(
            'import_transaction_id', 'writeoff_analytic_id',
            type='many2one', relation='account.analytic.account',
            string='Write-off analytic account'),
        'analytic_account_id': fields.related(
            'statement_line_id', 'analytic_account_id',
            type='many2one', relation='account.analytic.account',
            string="Analytic Account"),
        'move_currency_amount': fields.related('import_transaction_id','move_currency_amount',
            type='float', string='Match Currency Amount', readonly=True),
        #'manual_payment_order_id': fields.many2one(
        #    'payment.order', "Payment order to reconcile"),
        }

banking_transaction_wizard()

