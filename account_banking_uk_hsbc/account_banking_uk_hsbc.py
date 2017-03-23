# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    Copyright (C) 2011 credativ Ltd (<http://www.credativ.co.uk>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from datetime import date

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT


class hsbc_export(orm.Model):
    """HSBC Export"""
    _name = 'banking.export.hsbc'
    _description = __doc__
    _rec_name = 'execution_date'

    _columns = {
        'payment_order_ids': fields.many2many(
            'payment.order',
            'account_payment_order_hsbc_rel',
            'banking_export_hsbc_id', 'account_order_id',
            'Payment Orders',
            readonly=True),
        'identification':
            fields.char('Identification', size=15, readonly=True, select=True),
        'execution_date':
            fields.date('Execution Date', readonly=True),
        'no_transactions':
            fields.integer('Number of Transactions', readonly=True),
        'total_amount':
            fields.float('Total Amount', readonly=True),
        'date_generated':
            fields.datetime('Generation Date', readonly=True, select=True),
        'file':
            fields.binary('HSBC File', readonly=True),
        'state':
            fields.selection([
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('done', 'Reconciled'),
            ], 'State', readonly=True),
    }

    _defaults = {
        'date_generated': lambda *a: date.today().strftime(OE_DATEFORMAT),
        'state': 'draft',
    }


class payment_line(orm.Model):
    """The standard payment order is using a mixture of details from the
    partner record and the res.partner.bank record. For, instance, the account
    holder name is coming from the res.partner.bank record, but the company
    name and address are coming from the partner address record. This is
    problematic because the HSBC payment format is validating for alphanumeric
    characters in the company name and address. So, "Great Company Ltd." and
    "Great Company s.a." will cause an error because they have full-stops in
    the name.

    A better approach is to use the name and address details from the
    res.partner.bank record always. This way, the address details can be
    sanitized for the payments, whilst being able to print the proper name and
    address throughout the rest of the system e.g. on invoices.
    """

    _inherit = 'payment.line'

    def info_owner(self, cr, uid, ids, name=None, args=None, context=None):

        if not ids:
            return {}

        result = {}
        info = ''
        for line in self.browse(cr, uid, ids, context=context):
            owner = line.order_id.mode.bank_id

            name = owner.owner_name or owner.partner_id.name
            st = owner.street and owner.street or ''
            st1 = ''  # no street2 in res.partner.bank
            zip = owner.zip and owner.zip or ''
            city = owner.city and owner.city or ''
            zip_city = zip + ' ' + city
            cntry = owner.country_id and owner.country_id.name or ''
            info = name + "\n".join((st + " ", st1, zip_city, cntry))
            result[line.id] = info
        return result

    def info_partner(self, cr, uid, ids, name=None, args=None, context=None):
        if not ids:
            return {}
        result = {}
        info = ''

        for line in self.browse(cr, uid, ids, context=context):
            partner = line.bank_id

            name = partner.owner_name or partner.partner_id.name
            st = partner.street and partner.street or ''
            st1 = ''  # no street2 in res.partner.bank
            zip = partner.zip and partner.zip or ''
            city = partner.city and partner.city or ''
            zip_city = zip + ' ' + city
            cntry = partner.country_id and partner.country_id.name or ''
            info = name + "\n".join((st + " ", st1, zip_city, cntry))
            result[line.id] = info

        return result

    # Define the info_partner and info_owner so we can override the methods
    _columns = {
        'info_owner': fields.function(
            info_owner,
            string="Owner Account",
            type="text",
            help='Address of the Main Partner',
        ),
        'info_partner': fields.function(
            info_partner,
            string="Destination Account",
            type="text",
            help='Address of the Ordering Customer.'
        ),
    }
