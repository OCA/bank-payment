# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm
from openerp.tools.translate import _


class res_partner_bank(orm.Model):
    _inherit = 'res.partner.bank'

    def _check_bank(self, cr, uid, ids, context=None):
        # suppress base_iban's constraint to enforce BICs for IBANs
        # workaround for lp:933472
        return True

    def _constr_bank_message(self, cr, uid, ids, context=None):
        return _('\nPlease define BIC/Swift code on bank for bank '
                 'type IBAN Account to make valid payments')

    # Redefine constraint to update its function reference
    _constraints = [
        (_check_bank, _constr_bank_message, ['bic']),
    ]
