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
from openerp.addons.account_banking_iban_lookup import online


class ResBank(orm.Model):
    _inherit = 'res.bank'

    def online_bank_info(self, cr, uid, bic, context=None):
        """
        Overwrite existing API hook from account_banking
        """
        return online.bank_info(bic)

    def onchange_bic(
            self, cr, uid, ids, bic, name, context=None):

        if not bic:
            return {}

        info, address = online.bank_info(bic)
        if not info:
            return {}

        if address and address.country_id:
            country_ids = self.pool.get('res.country').search(
                cr, uid, [('code', '=', address.country_id)])
            country_id = country_ids[0] if country_ids else False
        else:
            country_id = False

        return {
            'value': dict(
                # Only the first eight positions of BIC are used for bank
                # transfers, so ditch the rest.
                bic=info.bic[:8],
                street=address.street,
                street2=address.get('street2', False),
                zip=address.zip,
                city=address.city,
                country=country_id,
                name=name or info.name,
            )
        }
