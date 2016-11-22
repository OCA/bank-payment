# coding: utf-8
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#
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

from openerp.osv import orm


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def def_journal_account_bank(
            self, cr, uid, ids, get_property_account, context=None):
        """
        Returns the property journal account for the given partners ids.

        :param get_property_account: method of this object that takes
        a partner browse record and returns a field name of type many2one.
        """
        if not ids:
            return {}
        res = dict([(res_id, False) for res_id in ids])
        for partner in self.browse(cr, uid, ids, context=context):
            property_account = get_property_account(partner)
            if partner[property_account]:
                res[partner.id] = partner[property_account].id
        return res

    def get_property_account_decrease(self, partner):
        if partner.customer and not partner.supplier:
            return 'property_account_receivable'
        return 'property_account_payable'

    def get_property_account_increase(self, partner):
        if partner.supplier and not partner.customer:
            return 'property_account_payable'
        return 'property_account_receivable'

    def def_journal_account_bank_decr(
            self, cr, uid, ids, context=None):
        """
        Return the default journal account to be used for this partner
        in the case of bank transactions that decrease the balance.
        """
        return self.def_journal_account_bank(
            cr, uid, ids, self.get_property_account_decrease, context=context)

    def def_journal_account_bank_incr(
            self, cr, uid, ids, context=None):
        """
        Return the default journal account to be used for this partner
        in the case of bank transactions that increase the balance.
        """
        return self.def_journal_account_bank(
            cr, uid, ids, self.get_property_account_increase, context=context)
