# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment that pays invoices module for OpenERP
#    Copyright (C) 2015 VisionDirect (http://www.visiondirect.co.uk)
#    @author Matthieu Choplin <matthieu.choplin@visiondirect.co.uk>
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
from datetime import date
from openerp.osv import osv
from openerp.tools.translate import _


class payment_order(osv.osv):
    _inherit = 'payment.order'

    def get_payment_ref(self, cr, uid, ids):
        return "Payment " + date.today().strftime("%d/%m/%y")

    _defaults = {
        'reference': get_payment_ref,
    }

    def create_bs(self, cr, uid, bank_journal):
        bs = self.pool.get('account.bank.statement')
        bank_stmt_id = bs.create(cr, uid, {
            'journal_id': bank_journal,
        })
        return bank_stmt_id

    def create_bsline(
            self, cr, uid,
            obj, invoice_record, bank_stmt_id, amount=0.0,
            amount_currency=0.0, currency_id=None
    ):
        bsl = self.pool.get('account.bank.statement.line')
        number = invoice_record.number or ""
        supplier_invoice_number = invoice_record.supplier_invoice_number or ""
        bank_stmt_line_id = bsl.create(cr,
                                       uid,
                                       {'ref': obj.reference,
                                        'name': number + " " + supplier_invoice_number,
                                        'statement_id': bank_stmt_id,
                                        'partner_id': invoice_record.partner_id.id,
                                        'amount': -amount,
                                        'amount_currency': -amount_currency,
                                        'currency_id': currency_id,
                                        })
        return bank_stmt_line_id

    def reconcile(
            self, cr, uid,
            invoice_record, bank_stmt_line_id, amount,
            amount_currency, currency_id
    ):
        # reconcile the payment with the invoice
        data_obj = self.pool.get('ir.model.data')
        bsl = self.pool.get('account.bank.statement.line')
        line_id = False
        for line in invoice_record.move_id.line_id:
            if line.account_id.user_type.id == data_obj.get_object_reference(
                    cr, uid, 'account', 'data_account_type_payable'
            )[1]:
                line_id = line
                break
        if not line_id:
            raise osv.except_osv(
                _('Warning!'),
                _("The journal entry '%s' for the invoice '%s' does "
                  "not have a line with an account receivable." % (
                      invoice_record.move_id.name, invoice_record.number
                  ))
            )
        amount_in_widget = currency_id and amount_currency or amount
        bsl.process_reconciliation(cr,
                                   uid,
                                   bank_stmt_line_id,
                                   [{'counterpart_move_line_id': line_id.id,
                                     'credit': amount_in_widget < 0 and -amount_in_widget or 0.0,
                                     'debit': amount_in_widget > 0 and amount_in_widget or 0.0,
                                     'name': line_id.name,
                                     }])
        return bank_stmt_line_id

    def set_done(self, cr, uid, ids, *args):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(payment_order, self).set_done(cr, uid, ids, *args)
        bs = self.pool.get('account.bank.statement')
        for obj in self.browse(cr, uid, ids):
            bank_journal = obj.mode.journal.id
            total_amount = 0.0
            # create the bank statement
            bank_stmt_id = self.create_bs(cr, uid, bank_journal)
            line_ids = obj.line_ids
            for line in line_ids:
                currency_id = None
                invoice = line.move_line_id.invoice
                if not invoice:
                    raise osv.except_osv(
                        _('Warning!'), _(
                            "The line {0} is not associated to any invoice.".format(
                                line.id)))
                if invoice.state == 'paid':
                    payments = ' '.join(
                        [l.move_id.name for l in invoice.payment_ids]
                    )
                    raise osv.except_osv(
                        _('Warning!'),
                        _("The invoice {0} has already been paid: {1}".format(
                            invoice.number, payments
                        ))
                    )
                amount_currency = line.amount_currency
                amount = line.amount
                if line.currency.id != line.company_currency.id:
                    currency_id = line.currency.id
                # bank statement line
                bank_stmt_line_id = self.create_bsline(
                    cr,
                    uid,
                    obj,
                    invoice,
                    bank_stmt_id,
                    amount,
                    amount_currency,
                    currency_id)
                self.reconcile(
                    cr,
                    uid,
                    invoice,
                    bank_stmt_line_id,
                    amount,
                    amount_currency,
                    currency_id)
                total_amount += amount
            bs.write(
                cr, uid, bank_stmt_id, {
                    'balance_end_real': -total_amount})
            bs.button_confirm_bank(cr, uid, [bank_stmt_id])
        return res
