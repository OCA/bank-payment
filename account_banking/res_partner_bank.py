# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2014 Therp BV (<http://therp.nl>).
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
from openerp.addons.account_banking import sepa


class ResPartnerBank(orm.Model):
    _inherit = 'res.partner.bank'

    def online_account_info(
            self, cr, uid, country_code, acc_number, context=None):
        """
        API hook for legacy online lookup of account info, 
        to be removed in OpenERP 8.0.
        """
        return False

    def search(self, cr, uid, args, *rest, **kwargs):
        '''
        Overwrite search, as both acc_number and iban now can be filled, so
        the original base_iban 'search and search again fuzzy' tactic now can
        result in doubled findings. Also there is now enough info to search
        for local accounts when a valid IBAN was supplied.
        
        Chosen strategy: create complex filter to find all results in just
                         one search
        '''

        def is_term(arg):
            '''Flag an arg as term or otherwise'''
            return isinstance(arg, (list, tuple)) and len(arg) == 3

        def extended_filter_term(term):
            '''
            Extend the search criteria in term when appropriate.
            '''
            extra_terms = []
            if term[0].lower() == 'acc_number' and term[1] in ('=', '=='):
                iban = sepa.IBAN(term[2])
                import pdb
                pdb.set_trace()
                if iban.valid:
                    extra_terms.append(('acc_number', term[1], iban.__repr__()))
                    if 'acc_number_domestic' in self._columns:
                        # Some countries can't convert to BBAN
                        try:
                            bban = iban.localized_BBAN
                            # Prevent empty search filters
                            if bban:
                                extra_terms.append(('acc_number_domestic', term[1], bban))
                        except:
                            pass
            result = [term]
            for extra_term in extra_terms:
                result = ['|'] + result + [extra_term]
            return result

        def extended_search_expression(args):
            '''
            Extend the search expression in args when appropriate.
            The expression itself is in reverse polish notation, so recursion
            is not needed.
            '''
            if not args:
                return []

            all = []
            if is_term(args[0]) and len(args) > 1:
                # Classic filter, implicit '&'
                all += ['&']
            
            for arg in args:
                if is_term(arg):
                    all += extended_filter_term(arg)
                else:
                    all += arg
            return all

        # Extend search filter
        newargs = extended_search_expression(args)
        
        # Original search
        results = super(ResPartnerBank, self).search(
            cr, uid, newargs, *rest, **kwargs)
        return results
