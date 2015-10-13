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
        """
        Disregard spaces when comparing IBANs.
        """

        def is_term(arg):
            '''Flag an arg as term or otherwise'''
            return isinstance(arg, (list, tuple)) and len(arg) == 3

        def extended_filter_term(term):
            '''
            Extend the search criteria in term when appropriate.
            '''
            result = [term]
            extra_terms = []
            if term[0].lower() == 'acc_number' and term[1] in ('=', '=='):
                iban = sepa.IBAN(term[2])
                if iban.valid:
                    # Disregard spaces when comparing IBANs
                    cr.execute(
                        """
                        SELECT id FROM res_partner_bank
                        WHERE replace(acc_number, ' ', '') = %s
                        """, (term[2].replace(' ', ''),))
                    ids = [row[0] for row in cr.fetchall()]
                    result = [('id', 'in', ids)]
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

            result = []
            if is_term(args[0]) and len(args) > 1:
                # Classic filter, implicit '&'
                result += ['&']

            for arg in args:
                if is_term(arg):
                    result += extended_filter_term(arg)
                else:
                    result += arg
            return result

        # Extend search filter
        newargs = extended_search_expression(args)

        # Original search
        return super(ResPartnerBank, self).search(
            cr, uid, newargs, *rest, **kwargs)
