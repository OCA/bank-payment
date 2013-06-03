# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#            
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'
    _columns = {
        'match_type': fields.related(
            # Add payment and storno types
            'import_transaction_id', 'match_type', type='selection',
            selection=[('manual', 'Manual'), ('move','Move'),
                       ('invoice', 'Invoice'), ('payment', 'Payment'),
                       ('payment_order', 'Payment order'),
                       ('storno', 'Storno')], 
            string='Match type', readonly=True,),
        }
