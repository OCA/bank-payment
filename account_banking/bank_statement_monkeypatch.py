# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, an open source suite of business applications
#    Copyright (C) 2004-2014 Odoo S.A.
#    Modifications Copyright (C) 2014 Banking addons community
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
# Monkeypatch based on non-compliant core code, therefore
# flake8: noqa
from openerp import netsvc
from openerp.osv import orm
from openerp.addons.account_voucher.account_voucher import account_bank_statement


def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, next_number, context=None):
    """
    Modified version of the method in account_voucher/account_voucher.py,
    which assigns the bank statement period to the voucher.

    As monkeypatching affects all databases of the instance, take care not
    to mess up on databases which do not have the period_id on the statement
    line.
    """
    if True: # align the indentation level with the original method
        voucher_obj = self.pool.get('account.voucher')
        wf_service = netsvc.LocalService("workflow")
        move_line_obj = self.pool.get('account.move.line')
        bank_st_line_obj = self.pool.get('account.bank.statement.line')
        st_line = bank_st_line_obj.browse(cr, uid, st_line_id, context=context)
        # <change>
        period_id = st_line.statement_id.period_id.id
        if 'period_id' in st_line._columns and st_line.period_id:
            period_id = st_line.period_id.id
        # </change>
        if st_line.voucher_id:
            voucher_obj.write(cr, uid, [st_line.voucher_id.id],
                            {'number': next_number,
                            'date': st_line.date,
                             # <change>
                             # 'period_id': statement_id.period_id.id},
                            'period_id': period_id},
                             # </change>
                            context=context)
            if st_line.voucher_id.state == 'cancel':
                voucher_obj.action_cancel_draft(cr, uid, [st_line.voucher_id.id], context=context)
            wf_service.trg_validate(uid, 'account.voucher', st_line.voucher_id.id, 'proforma_voucher', cr)

            v = voucher_obj.browse(cr, uid, st_line.voucher_id.id, context=context)
            bank_st_line_obj.write(cr, uid, [st_line_id], {
                'move_ids': [(4, v.move_id.id, False)]
            })

            return move_line_obj.write(cr, uid, [x.id for x in v.move_ids], {'statement_id': st_line.statement_id.id}, context=context)
        return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line.id, company_currency_id, next_number, context=context)


class BankStatementMonkeypatch(orm.AbstractModel):
    _name = 'account.bank.statement.monkeypatch'
    _description = 'Bank statement monkeypatch'

    def _register_hook(self, cr):
        account_bank_statement.create_move_from_st_line = create_move_from_st_line
        return super(BankStatementMonkeypatch, self)._register_hook(cr)
