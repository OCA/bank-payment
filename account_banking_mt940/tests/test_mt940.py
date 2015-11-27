# -*- coding: utf-8 -*-
"""Test MT940 parser."""
##############################################################################
#
#    Copyright (C) 2015 Therp BV <http://therp.nl>.
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
from openerp.tests.common import SingleTransactionCase
from openerp.addons.account_banking_mt940.mt940 import get_subfields


class TestMT940(SingleTransactionCase):

    def check_subfields(self, reg, cr, uid):
        """Check splitting of structured field in subfields."""
        data = (
            "/BENM//NAME/Kosten/REMI/Periode 01-10-2013 t/m 31-12-2013/ISDT/20"
        )
        codewords = ['BENM', 'ADDR', 'NAME', 'CNTP', 'ISDT', 'REMI']
        subfields = get_subfields(data, codewords)
        self.assertEqual(
            subfields['NAME'], ['Kosten'])
        self.assertEqual(
            subfields['REMI'], ['Periode 01-10-2013 t', 'm 31-12-2013'])
        self.assertEqual(
            subfields['ISDT'], ['20'])

    def test_mt940(self):
        reg, cr, uid, = self.registry, self.cr, self.uid
        # Tests might fail if admin does not have the English language
        reg('res.users').write(cr, uid, uid, {'lang': 'en_US'})
        self.check_subfields(reg, cr, uid)
