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
from openerp.report import report_sxw


class deposit_ticket_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(deposit_ticket_webkit, self).__init__(
            cr, uid, name, context=context
        )
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
        })


report_sxw.report_sxw(
    'report.deposit.ticket.webkit',
    'deposit.ticket',
    'addons/deposit_ticket_report_webkit/report/deposit_ticket.mako',
    parser=deposit_ticket_webkit
)
