##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    Copyright (C) 2012 credativ, Ltd (<http://www.credativ.co.uk>).
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
from datetime import date
from tools.translate import _

class payment_order(osv.osv):
    '''
    Attach export_clieop wizard to payment order and allow traceability
    '''
    _inherit = 'payment.order'
    def get_wizard(self, type):
        if type in ['UKACH', 'UKFP', 'UKPP']:
            return self._module, 'model_banking_export_hsbc_wizard'
        return super(payment_order, self).get_wizard(type)
payment_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
