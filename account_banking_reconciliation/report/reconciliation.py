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
from openerp.report import report_sxw
from openerp.addons.report_webkit import webkit_report


class Reconciliation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Reconciliation, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_debt_move_line_ids': self.get_debt_move_line_ids,
            'get_credit_move_line_ids': self.get_credit_move_line_ids
        })

    def get_debt_move_line_ids(self, record, cleared=True):
        return [
            line for line in record.debit_move_line_ids
            if line.cleared_bank_account is cleared
        ]

    def get_credit_move_line_ids(self, record, cleared=True):
        return [
            line for line in record.credit_move_line_ids
            if line.cleared_bank_account is cleared
        ]

report_name = 'report.detailed.reconciliation.webkit'

webkit_report.WebKitParser(
    report_name,
    'bank.acc.rec.statement',
    'addons/account_banking_reconciliation/'
    'report/detailed_reconciliation.mako',
    parser=Reconciliation,
)

report_name = 'report.summary.reconciliation.webkit'

webkit_report.WebKitParser(
    report_name,
    'bank.acc.rec.statement',
    'addons/account_banking_reconciliation/report/summary_reconciliation.mako',
    parser=Reconciliation
)
