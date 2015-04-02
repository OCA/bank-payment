# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time
from datetime import datetime, timedelta

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp.report import report_sxw
import openerp.addons.decimal_precision as dp


class bank_acc_rec_statement(orm.Model):

    """Bank account rec statement."""

    def check_group(self, cr, uid, ids, context=None):
        """
        Check if following security constraints are implemented for groups.

        Bank Statement Preparer - they can create, view and delete any of
        the Bank Statements provided the Bank Statement is not in the DONE
        state, or the Ready for Review state.

        Bank Statement Verifier - they can create, view, edit, and delete any
        of the Bank Statements information at any time.

        NOTE: DONE Bank Statements  are only allowed to be deleted by a Bank
        Statement Verifier.
        """
        model_data_obj = self.pool.get('ir.model.data')
        res_groups_obj = self.pool.get('res.groups')
        group_verifier_id = model_data_obj._get_id(
            cr, uid,
            'account_banking_reconciliation', 'group_bank_stmt_verifier'
        )
        for statement in self.browse(cr, uid, ids, context=context):
            if group_verifier_id:
                res_id = model_data_obj.read(
                    cr, uid, [group_verifier_id], ['res_id']
                )[0]['res_id']
                group_verifier = res_groups_obj.browse(
                    cr, uid, res_id, context=context
                )
                group_user_ids = [user.id for user in group_verifier.users]
                if statement.state != 'draft' and uid not in group_user_ids:
                    raise orm.except_orm(
                        _('User Error'),
                        _(
                            "Only a member of '%s' group may delete/edit "
                            "bank statements when not in draft state!" %
                            (group_verifier.name)
                        )
                    )
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}

        default.update({
            'credit_move_line_ids': [],
            'debit_move_line_ids': [],
            'name': '',
        })
        return super(bank_acc_rec_statement, self).copy(
            cr, uid, id, default=default, context=context
        )

    def create(self, cr, uid, vals, context=None):
        if "exchange_date" in vals and "account_id" in vals:
            vals.update(
                self.onchange_exchange_date(
                    cr, uid, [],
                    vals["exchange_date"], vals["account_id"],
                    context=context)['value'])

        base_func = super(bank_acc_rec_statement, self).create
        return base_func(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # Check if the user is allowed to perform the action
        self.check_group(cr, uid, ids, context)
        res = super(bank_acc_rec_statement, self).write(
            cr, uid, ids, vals, context=context
        )

        if "exchange_date" in vals:
            for stmt in self.browse(cr, uid, ids, context=context):
                stmt.write(self.onchange_exchange_date(
                    cr, uid, [],
                    stmt.exchange_date, stmt.account_id.id,
                    context=context)['value'])

        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        Reset the related account.move.line to be re-assigned later
        to statement.
        """
        statement_line_obj = self.pool.get('bank.acc.rec.statement.line')
        # Check if the user is allowed to perform the action
        self.check_group(cr, uid, ids, context)
        for statement in self.browse(cr, uid, ids, context=context):
            statement_lines = (
                statement.credit_move_line_ids +
                statement.debit_move_line_ids
            )
            statement_line_ids = map(lambda x: x.id, statement_lines)
            # call unlink method to reset
            statement_line_obj.unlink(
                cr, uid, statement_line_ids, context=context
            )
        return super(bank_acc_rec_statement, self).unlink(
            cr, uid, ids, context=context
        )

    def check_difference_balance(self, cr, uid, ids, context=None):
        """Check if difference balance is zero or not."""
        for statement in self.browse(cr, uid, ids, context=context):
            if statement.difference != 0.0 and not statement.multi_currency:
                raise orm.except_orm(
                    _('Warning!'),
                    _(
                        "Prior to reconciling a statement, all differences "
                        "must be accounted for and the Difference balance "
                        "must be zero. Please review and make necessary "
                        "changes."
                    )
                )
            elif (statement.difference_in_currency != 0.0 and
                    statement.multi_currency):
                raise orm.except_orm(
                    _('Warning'),
                    _('Prior to reconciling a statement in a foreign currency'
                      ', all differences must be accounted for and the '
                      'Difference in currency balance must be zero. Please '
                      'review and make necessary changes.'))
            elif (statement.multi_currency and
                    statement.general_ledger_balance !=
                    statement.registered_balance):
                raise orm.except_orm(
                    _('Warning'),
                    _('Prior to reconciling a statement in a foreign currency'
                      ', you should make sure the general ledger balance and '
                      'registered balance match. If necessary, an adjustment '
                      'move can be created to account for the difference.'))
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """Cancel the the statement."""
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_review(self, cr, uid, ids, context=None):
        """Change the status of statement from 'draft' to 'to_be_reviewed'."""
        # If difference balance not zero prevent further processing
        self.check_difference_balance(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'to_be_reviewed'}, context=context)
        return True

    def action_process(self, cr, uid, ids, context=None):
        """
        Set the account move lines as 'Cleared' and Assign
        'Bank Acc Rec Statement ID' for the statement lines which
        are marked as 'Cleared'.
        """
        account_move_line_obj = self.pool.get('account.move.line')
        # If difference balance not zero prevent further processing
        self.check_difference_balance(cr, uid, ids, context=context)
        for statement in self.browse(cr, uid, ids, context=context):
            statement_lines = (
                statement.credit_move_line_ids +
                statement.debit_move_line_ids
            )
            for statement_line in statement_lines:
                # Mark the move lines as 'Cleared'mand assign
                # the 'Bank Acc Rec Statement ID'
                if statement_line.move_line_id:
                    account_move_line_obj.write(
                        cr, uid,
                        [statement_line.move_line_id.id],
                        {
                            'cleared_bank_account': (
                                statement_line.cleared_bank_account
                            ),
                            'bank_acc_rec_statement_id': (
                                statement_line.cleared_bank_account and
                                statement.id or
                                False
                            ),
                        },
                        context=context
                    )

            self.write(
                cr, uid,
                [statement.id],
                {
                    'state': 'done',
                    'verified_by_user_id': uid,
                    'verified_date': time.strftime('%Y-%m-%d')
                },
                context=context
            )
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        """Reset the statement to draft and perform resetting operations."""
        account_move_line_obj = self.pool.get('account.move.line')
        for statement in self.browse(cr, uid, ids, context=context):
            statement_lines = (
                statement.credit_move_line_ids +
                statement.debit_move_line_ids
            )
            line_ids = []
            statement_line_ids = []
            for statement_line in statement_lines:
                statement_line_ids.append(statement_line.id)
                if statement_line.move_line_id.id:
                    # Find move lines related to statement lines
                    line_ids.append(statement_line.move_line_id.id)

            # Reset 'Cleared' and 'Bank Acc Rec Statement ID' to False
            account_move_line_obj.write(
                cr, uid,
                line_ids,
                {
                    'cleared_bank_account': False,
                    'bank_acc_rec_statement_id': False,
                },
                context=context
            )
            # Reset statement
            self.write(
                cr, uid,
                [statement.id],
                {
                    'state': 'draft',
                    'verified_by_user_id': False,
                    'verified_date': False
                },
                context=context
            )

        return True

    def action_select_all(self, cr, uid, ids, context=None):
        """Mark all the statement lines as 'Cleared'."""
        statement_line_obj = self.pool.get('bank.acc.rec.statement.line')
        for statement in self.browse(cr, uid, ids, context=context):
            statement_lines = (
                statement.credit_move_line_ids +
                statement.debit_move_line_ids
            )
            statement_line_ids = map(lambda x: x.id, statement_lines)
            statement_line_obj.write(
                cr, uid,
                statement_line_ids,
                {'cleared_bank_account': True},
                context=context
            )
        return True

    def action_unselect_all(self, cr, uid, ids, context=None):
        """Reset 'Cleared' in all the statement lines."""
        statement_line_obj = self.pool.get('bank.acc.rec.statement.line')
        for statement in self.browse(cr, uid, ids, context=context):
            statement_lines = (
                statement.credit_move_line_ids +
                statement.debit_move_line_ids
            )
            statement_line_ids = map(lambda x: x.id, statement_lines)
            statement_line_obj.write(
                cr, uid,
                statement_line_ids,
                {'cleared_bank_account': False},
                context=context
            )
        return True

    def action_adjust_ending_balance(self, cr, uid, ids, context=None):
        account_move_obj = self.pool["account.move"]
        period_obj = self.pool["account.period"]
        for stmt in self.browse(cr, uid, ids, context=context):
            if stmt.adjustment_move_id:
                continue

            company = stmt.company_id
            move_line = {
                'name': _('Adjustment for reconciliation %s') % (stmt.name, ),
                'account_id': stmt.account_id.id,
                'cleared_bank_account': True,
            }
            reverse_move = {'name': move_line['name']}
            amount = abs(stmt.general_ledger_balance - stmt.registered_balance)
            if stmt.general_ledger_balance < stmt.registered_balance:
                account = company.income_currency_exchange_account_id
                if not account:
                    raise orm.except_orm(
                        _("No Gain Exchange Rate Account"),
                        _("You need to configure the Gain Exchange Rate "
                          "Account for the company in order to create an"
                          " adjustment move"))
                move_line['debit'] = amount
                reverse_move['credit'] = amount
                reverse_move['account_id'] = account.id
            elif stmt.registered_balance < stmt.general_ledger_balance:
                account = company.expense_currency_exchange_account_id
                if not account:
                    raise orm.except_orm(
                        _("No Gain Exchange Rate Account"),
                        _("You need to configure the Gain Exchange Rate "
                          "Account for the company in order to create an"
                          " adjustment move"))
                move_line['credit'] = amount
                reverse_move['debit'] = amount
                reverse_move['account_id'] = account.id
            else:
                raise orm.except_orm(
                    _("Adjustment Unnecessary"),
                    _("The General Ledger Balance and Registered Balance "
                      "are equal, no adjustment necessary."))

            if not company.default_cutoff_journal_id:
                raise orm.except_orm(
                    _("No Default Cut-off Journal"),
                    _("You need to set the Default Cut-off Journal for your "
                      "company to create an adjustment move"))

            period_id = period_obj.find(cr, uid, stmt.ending_date,
                                        context=context)[0]
            move_id = account_move_obj.create(
                cr, uid, {
                    'ref': stmt.name,
                    'period_id': period_id,
                    'date': stmt.ending_date,
                    'journal_id': company.default_cutoff_journal_id.id,
                    'line_id': [(0, 0, move_line),
                                (0, 0, reverse_move)],
                },
                context=context)
            account_move_obj.button_validate(cr, uid, [move_id],
                                             context=context)
            stmt.write({'adjustment_move_id': move_id})
        return True

    def _get_balance(self, cr, uid, ids, field_names, args, context=None):
        """
        Computed as following:
        A) Deposits, Credits, and Interest Amount:
           Total SUM of Amts of lines with Cleared = True
        Deposits, Credits, and Interest # of Items:
        Total of number of lines with Cleared = True
        B) Checks, Withdrawals, Debits, and Service Charges Amount:
        Checks, Withdrawals, Debits, and Service Charges Amount # of Items:
        Cleared Balance (Total Sum of the Deposit Amount Cleared (A) -
        Total Sum of Checks Amount Cleared (B))
        Difference= (Ending Balance - Beginning Balance) -
        cleared balance = should be zero.
        """
        res = {}
        account_precision = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account'
        )
        for statement in self.browse(cr, uid, ids, context=context):

            res[statement.id] = sres = {
                'sum_of_credits': 0.0,
                'sum_of_credits_in_currency': 0.0,
                'sum_of_credits_lines': 0.0,
                'sum_of_debits': 0.0,
                'sum_of_debits_in_currency': 0.0,
                'sum_of_debits_lines': 0.0,
                'sum_of_credits_unclear': 0.0,
                'sum_of_credits_unclear_in_currency': 0.0,
                'sum_of_credits_lines_unclear': 0.0,
                'sum_of_debits_unclear': 0.0,
                'sum_of_debits_unclear_in_currency': 0.0,
                'sum_of_debits_lines_unclear': 0.0,
                'uncleared_balance': 0.0,
                'uncleared_balance_in_currency': 0.0,
                'cleared_balance': 0.0,
                'cleared_balance_in_currency': 0.0,
                'difference': 0.0,
                'difference_in_currency': 0.0,
            }

            for line in statement.credit_move_line_ids:
                sum_credit = round(line.amount, account_precision)
                amount_cur = round(line.amount_in_currency, account_precision)
                if line.cleared_bank_account:
                    sres['sum_of_credits'] += sum_credit
                    sres['sum_of_credits_in_currency'] += amount_cur
                    sres['sum_of_credits_lines'] += 1.0
                else:
                    sres['sum_of_credits_unclear'] += sum_credit
                    sres['sum_of_credits_unclear_in_currency'] += amount_cur
                    sres['sum_of_credits_lines_unclear'] += 1.0

            for line in statement.debit_move_line_ids:
                sum_debit = round(line.amount, account_precision)
                amount_cur = round(line.amount_in_currency, account_precision)
                if line.cleared_bank_account:
                    sres['sum_of_debits'] += sum_debit
                    sres['sum_of_debits_in_currency'] += amount_cur
                    sres['sum_of_debits_lines'] += 1.0
                else:
                    sres['sum_of_debits_unclear'] += sum_debit
                    sres['sum_of_debits_unclear_in_currency'] += amount_cur
                    sres['sum_of_debits_lines_unclear'] += 1.0

            sres['cleared_balance'] = round(
                sres['sum_of_debits'] - sres['sum_of_credits'],
                account_precision)
            sres['cleared_balance_in_currency'] = round(
                (sres['sum_of_debits_in_currency']
                 - sres['sum_of_credits_in_currency']),
                account_precision)
            sres['uncleared_balance'] = round(
                sres['sum_of_debits_unclear'] - sres['sum_of_credits_unclear'],
                account_precision)
            sres['uncleared_balance_in_currency'] = round(
                (sres['sum_of_debits_unclear_in_currency']
                 - sres['sum_of_credits_unclear_in_currency']),
                account_precision)
            sres['difference'] = round(
                (statement.ending_balance - statement.starting_balance)
                - sres['cleared_balance'],
                account_precision)
            sres['difference_in_currency'] = round(
                (statement.ending_balance_in_currency
                 - sres['cleared_balance_in_currency']
                 - statement.starting_balance_in_currency),
                account_precision)
            sres['general_ledger_balance'] = self._get_gl_balance(
                cr, uid, statement.account_id.id, statement.ending_date)
            sres['registered_balance'] = round(
                (statement.starting_balance
                 + sres['cleared_balance']
                 + sres['uncleared_balance']),
                account_precision)

        return res

    def _get_gl_balance(self, cr, uid, account_id, date=None):
        """ Get the General Ledger balance at date for account """
        fyear_obj = self.pool["account.fiscalyear"]
        account_obj = self.pool['account.account']
        date = date or time.strftime('%Y-%m-%d')
        fiscal_yearid = fyear_obj.find(cr, uid, date)
        date_from = fyear_obj.browse(cr, uid, fiscal_yearid).date_start

        balance = account_obj.read(
            cr, uid, account_id, ['balance'],
            context={'date_from': date_from,
                     'date_to': date,
                     'state': 'posted'})
        return balance["balance"]

    def _get_move_line_write(self, line):
        res = {
            'ref': line.ref,
            'date': line.date,
            'partner_id': line.partner_id.id,
            'currency_id': line.currency_id.id,
            'amount': line.credit or line.debit,
            'name': line.name,
            'move_line_id': line.id,
            'type': line.credit and 'cr' or 'dr'
        }

        if line.credit:
            res['amount_in_currency'] = -line.amount_currency
        else:
            res['amount_in_currency'] = line.amount_currency

        return res

    def refresh_record(self, cr, uid, ids, context=None):
        account_move_line_obj = self.pool["account.move.line"]
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.account_id:
                continue

            to_write = {'credit_move_line_ids': [], 'debit_move_line_ids': []}
            # For existing records, allow refresh to set multi_currency
            # correctly by updating it during the refresh. This allows viewing
            # multi currency fields without changing the account
            acur = obj.account_id.currency_id
            ccur = obj.account_id.company_id.currency_id
            if acur and ccur and acur.id != ccur.id:
                to_write['multi_currency'] = True

            move_line_ids = [
                line.move_line_id.id
                for line in obj.credit_move_line_ids + obj.debit_move_line_ids
                if line.move_line_id
            ]

            domain = [
                ('id', 'not in', move_line_ids),
                ('account_id', '=', obj.account_id.id),
                ('move_id.state', '=', 'posted'),
                ('cleared_bank_account', '=', False),
                ('journal_id.type', '!=', 'situation'),
            ]

            # if not keep_previous_uncleared_entries:
            #     domain += [('draft_assigned_to_statement', '=', False)]

            if not obj.suppress_ending_date_filter:
                domain += [('date', '<=', obj.ending_date)]
            line_ids = account_move_line_obj.search(
                cr, uid, domain, context=context
            )
            lines = account_move_line_obj.browse(
                cr, uid, line_ids, context=context
            )
            for line in lines:
                if obj.keep_previous_uncleared_entries:
                    # only take bank_acc_rec_statement at state cancel or done
                    if not self.is_b_a_r_s_state_done(
                            cr, uid, line.id, context=context):
                        continue
                res = (0, 0, self._get_move_line_write(line))
                if line.credit:
                    to_write['credit_move_line_ids'].append(res)
                else:
                    to_write['debit_move_line_ids'].append(res)

            obj.write(to_write)

        return True

    def is_b_a_r_s_state_done(self, cr, uid, move_line_id, context=None):
        statement_line_obj = self.pool.get('bank.acc.rec.statement.line')
        statement_line_ids = statement_line_obj.search(
            cr, uid, [('move_line_id', '=', move_line_id)], context=context
        )
        for state_line in statement_line_ids:
            b_a_r_s_line = statement_line_obj.browse(
                cr, uid, state_line, context=context
            )
            b_a_r_s = self.browse(
                cr, uid, b_a_r_s_line.statement_id.id, context=context
            )
            if b_a_r_s and b_a_r_s.state not in ("done", "cancel"):
                return False
        return True

    def _get_last_reconciliation(self, cr, uid, account_id, context=None):
        res = self.search(cr, uid,
                          [('account_id', '=', account_id),
                           ('state', '!=', 'cancel')],
                          order="ending_date desc",
                          limit=1)
        if res:
            return self.browse(cr, uid, res[0], context=context)
        else:
            return None

    def onchange_account_id(
        self, cr, uid, ids, account_id, ending_date,
        suppress_ending_date_filter, keep_previous_uncleared_entries,
        context=None
    ):
        account_obj = self.pool['account.account']
        account_move_line_obj = self.pool.get('account.move.line')
        statement_line_obj = self.pool.get('bank.acc.rec.statement.line')
        val = {
            'value': {
                'credit_move_line_ids': [],
                'debit_move_line_ids': [],
                'multi_currency': False,
                'company_currency_id': False,
                'account_currency_id': False,
            }
        }
        if account_id:
            last_rec = self._get_last_reconciliation(cr, uid, account_id,
                                                     context=context)
            if last_rec and last_rec.ending_date:
                val['value']['exchange_date'] = (datetime.strptime(
                    last_rec.ending_date, DEFAULT_SERVER_DATE_FORMAT,
                ) + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            elif ending_date:
                # end_date - 1 month + 1 day
                dt_ending = datetime.strptime(
                    ending_date, DEFAULT_SERVER_DATE_FORMAT,
                ) + timedelta(days=-1)
                if dt_ending.month == 1:
                    dt_ending = dt_ending.replace(year=dt_ending.year - 1,
                                                  month=12)
                else:
                    dt_ending = dt_ending.replace(month=dt_ending.month - 1)
                val['value']['exchange_date'] = dt_ending.strftime(
                    DEFAULT_SERVER_DATE_FORMAT)

            account = account_obj.browse(cr, uid, account_id, context=context)
            acur = account.currency_id
            ccur = account.company_id.currency_id
            if acur and ccur and acur.id != ccur.id:
                val['value']['multi_currency'] = True

            for statement in self.browse(cr, uid, ids, context=context):
                statement_line_ids = statement_line_obj.search(
                    cr, uid,
                    [('statement_id', '=', statement.id)],
                    context=context
                )
                # call unlink method to reset and remove existing
                # statement lines and mark reset field values in
                # related move lines
                statement_line_obj.unlink(
                    cr, uid, statement_line_ids, context=context
                )

            # Apply filter on move lines to allow
            # 1. credit and debit side journal items in posted state
            #    of the selected GL account
            # 2. Journal items which are not assigned to previous
            #    bank statements
            # 3. Date less than or equal to ending date provided the
            #    'Suppress Ending Date Filter' is not checked
            # get previous uncleared entries
            domain = [
                ('account_id', '=', account_id),
                ('move_id.state', '=', 'posted'),
                ('cleared_bank_account', '=', False),
                ('journal_id.type', '!=', 'situation'),
            ]
            if not keep_previous_uncleared_entries:
                domain += [('draft_assigned_to_statement', '=', False)]

            if not suppress_ending_date_filter:
                domain += [('date', '<=', ending_date)]
            line_ids = account_move_line_obj.search(
                cr, uid, domain, context=context
            )
            for line in account_move_line_obj.browse(
                    cr, uid, line_ids, context=context):
                if keep_previous_uncleared_entries:
                    # only take bank_acc_rec_statement at state cancel or done
                    if not self.is_b_a_r_s_state_done(
                            cr, uid, line.id, context=context):
                        continue
                res = self._get_move_line_write(line)
                if res['type'] == 'cr':
                    val['value']['credit_move_line_ids'].append(res)
                else:
                    val['value']['debit_move_line_ids'].append(res)
        return val

    # This method almost extracted from account_voucher
    def _get_currency_help_label(self, cr, uid, currency_id, payment_rate,
                                 payment_rate_currency_id, context=None):
        """
        The function builds a string to help the users to understand the
        behavior of the payment rate fields they can specify on the voucher.
        This string is only used to improve the usability in the voucher form
        view and has no other effect.

        :param currency_id: the voucher currency
        :type currency_id: integer
        :param payment_rate: the value of the payment_rate field of the voucher
        :type payment_rate: float
        :param payment_rate_currency_id: the value of the
        payment_rate_currency_id field of the voucher
        :type payment_rate_currency_id: integer
        :return: translated string giving a tip on what's the effect of
        the current payment rate specified
        :rtype: str
        """
        rml_parser = report_sxw.rml_parse(cr, uid, 'currency_help_label',
                                          context=context)
        currency_pool = self.pool['res.currency']
        currency_str = payment_rate_str = ''
        if currency_id:
            currency_str = rml_parser.formatLang(
                1,
                currency_obj=currency_pool.browse(
                    cr, uid, currency_id, context=context
                )
            )
        if payment_rate_currency_id:
            payment_rate_str = rml_parser.formatLang(
                payment_rate,
                currency_obj=currency_pool.browse(
                    cr, uid, payment_rate_currency_id, context=context
                )
            )
        currency_help_label = _(
            'At the starting date, the exchange rate was\n%s = %s'
        ) % (currency_str, payment_rate_str)
        return currency_help_label

    def onchange_currency_rate(self, cr, uid, ids, exchange_rate,
                               start_balance, end_balance, context=None):
        if exchange_rate:
            return {
                'value': {
                    'starting_balance': (start_balance or 0) * exchange_rate,
                    'ending_balance': (end_balance or 0) * exchange_rate,
                }
            }
        else:
            return {}

    def onchange_exchange_date(self, cr, uid, ids, exchange_date, account_id,
                               context=None):
        currency_obj = self.pool['res.currency']
        account_obj = self.pool['account.account']
        res = {}
        res['value'] = val = {}
        if not account_id or not exchange_date:
            return res

        account = account_obj.browse(cr, uid, account_id)
        acur = account.currency_id
        ccur = account.company_id.currency_id
        if not acur or not ccur or acur.id == ccur.id:
            val['currency_rate'] = 1
            val['currency_help_label'] = ''
            val['multi_currency'] = False
        else:
            ctx2 = context.copy() if context else {}
            ctx2['date'] = exchange_date
            payment_rate = currency_obj._get_conversion_rate(
                cr, uid, acur, ccur, context=ctx2)
            val['currency_rate'] = payment_rate
            val['currency_rate_label'] = self._get_currency_help_label(
                cr, uid, acur.id, payment_rate, ccur.id, context)
            val['multi_currency'] = True

        return res

    _name = "bank.acc.rec.statement"
    _columns = {
        'name': fields.char(
            'Name',
            required=True,
            size=64,
            states={'done': [('readonly', True)]},
            help=(
                "This is a unique name identifying the statement "
                "(e.g. Bank X January 2012)."
            ),
        ),
        'multi_currency': fields.boolean('Multi-currency mode enabled'),
        'currency_conversion_date': fields.date('Currency Conversion Date'),
        'currency_rate': fields.float(
            'Currency Exchange Rate',
            digits=(12, 6),
        ),
        'currency_rate_label': fields.text('Currency Rate Message'),
        'account_id': fields.many2one(
            'account.account',
            'Account',
            required=True,
            states={'done': [('readonly', True)]},
            domain="[('company_id', '=', company_id), ('type', '!=', 'view')]",
            help="The Bank/Gl Account that is being reconciled."
        ),
        'exchange_date': fields.date(
            'Currency Exchange Date',
            required=False,
            states={'done': [('readonly', True)]},
            help="The starting date of your bank statement.",
        ),
        'ending_date': fields.date(
            'Ending Date',
            required=True,
            states={'done': [('readonly', True)]},
            help="The ending date of your bank statement."
        ),
        'starting_balance': fields.float(
            'Starting Balance',
            required=True,
            digits_compute=dp.get_precision('Account'),
            help="The Starting Balance on your bank statement, in your "
                 "company's currency",
            states={'done': [('readonly', True)]}
        ),
        'starting_balance_in_currency': fields.float(
            'Starting Balance in Currency',
            required=True,
            digits_compute=dp.get_precision('Account'),
            help="The Account Starting Balance on your bank statement",
            states={'done': [('readonly', True)]},
        ),
        'ending_balance': fields.float(
            'Ending Balance',
            required=True,
            digits_compute=dp.get_precision('Account'),
            help="The Ending Balance on your bank statement, in your "
                 "company's currency",
            states={'done': [('readonly', True)]}
        ),
        'ending_balance_in_currency': fields.float(
            'Ending Balance in Currency',
            required=True,
            digits_compute=dp.get_precision('Account'),
            help="The Ending Balance on your bank statement.",
            states={'done': [('readonly', True)]}
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True,
            readonly=True,
            help="The Company for which the deposit ticket is made to"
        ),
        'notes': fields.text('Notes'),
        'verified_date': fields.date(
            'Verified Date',
            states={'done': [('readonly', True)]},
            help="Date in which Deposit Ticket was verified."
        ),
        'verified_by_user_id': fields.many2one(
            'res.users',
            'Verified By',
            states={'done': [('readonly', True)]},
            help=(
                "Entered automatically by the “last user” who "
                "saved it. System generated."
            ),
        ),
        'credit_move_line_ids': fields.one2many(
            'bank.acc.rec.statement.line',
            'statement_id',
            'Credits',
            domain=[('type', '=', 'cr')],
            context={'default_type': 'cr'},
            states={'done': [('readonly', True)]}
        ),
        'debit_move_line_ids': fields.one2many(
            'bank.acc.rec.statement.line',
            'statement_id',
            'Debits',
            domain=[('type', '=', 'dr')],
            context={'default_type': 'dr'},
            states={'done': [('readonly', True)]}
        ),
        'cleared_balance': fields.function(
            _get_balance,
            method=True,
            string='Cleared Balance',
            digits_compute=dp.get_precision('Account'),
            type='float',
            help=(
                "Total Sum of the Deposit Amount Cleared – Total Sum of "
                "Checks, Withdrawals, Debits, and Service Charges "
                "Amount Cleared"
            ),
            multi="balance"
        ),
        'cleared_balance_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Cleared Balance',
            digits_compute=dp.get_precision('Account'),
            help="Total Sum of the Deposit Amount Cleared – Total Sum of "
                 "Checks, Withdrawals, Debits, and Service Charges Amount "
                 "Cleared",
            multi="balance",
        ),
        'difference': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Difference',
            digits_compute=dp.get_precision('Account'),
            help="(Ending Balance – Beginning Balance) - Cleared Balance.",
            multi="balance"
        ),
        'difference_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Difference',
            digits_compute=dp.get_precision('Account'),
            help="(Ending Balance – Beginning Balance) - Cleared Balance.",
            multi="balance",
        ),
        'sum_of_credits': fields.function(
            _get_balance,
            method=True,
            string='Checks, Withdrawals, Debits, and Service Charges Amount',
            digits_compute=dp.get_precision('Account'),
            type='float',
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_credits_in_currency': fields.function(
            _get_balance, method=True, type='float',
            string='Checks, Withdrawals, Debits, and Service Charges Amount'
                   'in currency',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance",
        ),
        'sum_of_debits': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest Amount',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_debits_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest Amount',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance",
        ),
        'sum_of_credits_lines': fields.function(
            _get_balance,
            method=True,
            string=(
                'Checks, Withdrawals, Debits, and Service Charges '
                '# of Items'
            ),
            type='float',
            help="Total of number of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_debits_lines': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest # of Items',
            help="Total of number of lines with Cleared = True",
            multi="balance"
        ),
        'uncleared_balance': fields.function(
            _get_balance,
            method=True,
            string='Uncleared Balance',
            digits_compute=dp.get_precision('Account'),
            type='float',
            help=(
                "Total Sum of the Deposit Amount Cleared – Total Sum "
                "of Checks, Withdrawals, Debits, and Service Charges "
                "Amount Cleared"
            ),
            multi="balance"
        ),
        'uncleared_balance_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Uncleared Balance',
            digits_compute=dp.get_precision('Account'),
            help="Total Sum of the Deposit Amount Cleared – Total Sum of "
                 "Checks, Withdrawals, Debits, and Service Charges Amount "
                 "Cleared",
            multi="balance",
        ),
        'sum_of_credits_unclear': fields.function(
            _get_balance,
            method=True,
            string='Checks, Withdrawals, Debits, and Service Charges Amount',
            digits_compute=dp.get_precision('Account'),
            type='float',
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_credits_unclear_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Checks, Withdrawals, Debits, and Service Charges Amount',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = False",
            multi="balance",
        ),
        'sum_of_debits_unclear': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest Amount',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_debits_unclear_in_currency': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest Amount',
            digits_compute=dp.get_precision('Account'),
            help="Total SUM of Amts of lines with Cleared = False",
            multi="balance",
        ),
        'sum_of_credits_lines_unclear': fields.function(
            _get_balance,
            method=True,
            string=(
                'Checks, Withdrawals, Debits, and Service '
                'Charges # of Items'
            ),
            type='float', help="Total of number of lines with Cleared = True",
            multi="balance"
        ),
        'sum_of_debits_lines_unclear': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Deposits, Credits, and Interest # of Items',
            help="Total of number of lines with Cleared = True",
            multi="balance"
        ),
        'general_ledger_balance': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='General Ledger Balance',
            digits_compute=dp.get_precision('Account'),
            help="General Ledger Balance",
            multi="balance"
        ),
        'registered_balance': fields.function(
            _get_balance,
            method=True,
            type='float',
            string='Registered Balance',
            digits_compute=dp.get_precision('Account'),
            help="Initial balance + Cleared Balance + Uncleared Balance",
            multi="balance"),
        'adjustment_move_id': fields.many2one(
            'account.move',
            'Adjustement Move',
            required=False,
            help="Adjustment move used to balance the General Ledger for "
                 "accounts in a secondary currency"),
        'suppress_ending_date_filter': fields.boolean(
            'Remove Ending Date Filter',
            help=(
                "If this is checked then the Statement End Date "
                "filter on the transactions below will not occur. "
                "All transactions would come over."
            ),
        ),
        'keep_previous_uncleared_entries': fields.boolean(
            'Keep Previous Uncleared Entries',
            help=(
                "If this is checked then the previous uncleared entries "
                "will be include."
            )
        ),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('to_be_reviewed', 'Ready for Review'),
                ('done', 'Done'),
                ('cancel', 'Cancel')
            ],
            'State',
            select=True,
            readonly=True
        ),
    }

    _defaults = {
        'state': 'draft',
        'company_id': (
            lambda self, cr, uid, c: self.pool.get('res.users').browse(
                cr, uid, uid, c
            ).company_id.id
        ),
        'ending_date': time.strftime('%Y-%m-%d'),
        'multi_currency': False,
        'keep_previous_uncleared_entries': True,
    }

    _order = "ending_date desc"
    _sql_constraints = [
        (
            'name_company_uniq',
            'unique (name, company_id, account_id)',
            (
                'The name of the statement must be unique per company '
                'and G/L account!'
            )
        )
    ]
