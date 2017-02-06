# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) SHS-AV s.r.l. (<http://www.zeroincombenze.it>)
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


from openerp.tests.common import SingleTransactionCase
import logging

__version__ = "0.1.1"
_logger = logging.getLogger(__name__)
INIT_PARTY_ISSUE = '1234567A'
COMPANY_BE_VAT = 'BE0477472701'
COMPANY_NL_VAT = 'NL123456782B90'
BNK_NL_BIC = 'INGBNL2A'
BNK_NL_NAME = 'ING Bank'
BNK_NL_ACC_NUMBER = 'NL08INGB0000000555'
COMPANY_IT_VAT = 'IT12345670017'
BNK_IT_BIC = 'BCITITMM300'
BNK_IT_NAME = 'Intesa San Paolo Ag.7 MI'
BNK_IT_ACC_NUMBER = 'IT31Z0306909420615282446606'


class Test_company(SingleTransactionCase):
    # Function with xt prefix are common library function
    # They help testing process
    def xtr(self, model):
        """Return object model to test
        """
        return self.registry(model)

    def write_ref(self, xid, values):
        """ Browse and write existent record for test
        """
        obj = self.browse_ref(xid)
        return obj.write(values)

    def xtcreate(self, model, values):
        """ Create a new record for test
        """
        return self.xtr(model).create(self.cr,
                                      self.uid,
                                      values)

    def setup_company(self, country_code=None):
        """Setup company (should be customized for specific country)
        """
        if country_code:
            self.country_code = country_code
        else:
            self.country_code = 'nl'
        xcountry = 'base.' + self.country_code
        self.country_id = self.ref(xcountry)
        if self.country_code == 'be':
            vals = {'initiating_party_issuer': INIT_PARTY_ISSUE,
                    'vat': COMPANY_BE_VAT}
        elif self.country_code == 'nl':
            vals = {'initiating_party_issuer': INIT_PARTY_ISSUE,
                    'vat': COMPANY_NL_VAT}
        elif self.country_code == 'it':
            vals = {'initiating_party_issuer': INIT_PARTY_ISSUE,
                    'vat': COMPANY_IT_VAT}
        else:
            vals = {'initiating_party_issuer': INIT_PARTY_ISSUE,
                    'vat': None}
        self.company = self.write_ref('base.main_company',
                                      vals)
        self.currency_id = self.ref('base.EUR')
        if self.country_code == 'nl':
            vals = {
                'name': BNK_NL_NAME,
                'bic': BNK_NL_BIC,
                'country': self.country_id,
            }
        elif self.country_code == 'it':
            vals = {
                'name': BNK_IT_NAME,
                'bic': BNK_IT_BIC,
                'country': self.country_id,
            }
        else:
            vals = {}
        self.bank_id = self.xtcreate('res.bank',
                                     vals)
        self.partner_id = self.ref('base.main_partner')
        self.company_id = self.ref('base.main_company')
        if self.country_code == 'nl':
            vals = {
                'state': 'iban',
                'acc_number': BNK_NL_ACC_NUMBER,
                'bank': self.bank_id,
                'bank_bic': BNK_NL_BIC,
                'partner_id': self.partner_id,
                'company_id': self.company_id,
            }
        elif self.country_code == 'it':
            vals = {
                'state': 'iban',
                'acc_number': BNK_IT_ACC_NUMBER,
                'bank': self.bank_id,
                'bank_bic': BNK_IT_BIC,
                'partner_id': self.partner_id,
                'company_id': self.company_id,
            }
        else:
            vals = {}
        self.partner_bank_id = self.xtcreate('res.partner.bank',
                                             vals)
        self.xtr('res.users').write(
            self.cr, self.uid, [self.uid],
            {'company_ids': [(4, self.company_id)]})
        self.xtr('res.users').write(
            self.cr, self.uid, [self.uid],
            {'company_id': self.company_id})
        self.partner_id = self.ref('base.res_partner_2')

    def setUp(self):
        self.setup_company()

    def test_company(self):
        cr, uid = self.cr, self.uid
        company_model = self.registry('res.company')
        if self.country_code == 'be':
            val = COMPANY_BE_VAT[2:]
        else:
            val = False
        res = company_model.\
            _get_initiating_party_identifier(cr,
                                             uid,
                                             self.company_id)
        assert res == val, \
            'Invalid "%s" party issuer: expected "%s"' % (res,
                                                          val)
