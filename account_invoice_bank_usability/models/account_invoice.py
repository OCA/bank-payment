# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Pexego (<http://www.pexego.es>).
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

from openerp import models, api
from lxml import etree


class account_invoice(models.Model):

    _inherit = "account.invoice"

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False,
                        submenu=False):
        context = self._context

        res = super(account_invoice, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)

        doc = etree.XML(res['arch'])

        if context.get('type'):
            for node in doc.xpath("//field[@name='partner_bank_id']"):
                if context['type'] in ('in_refund', 'out_refund'):
                    node.set('domain', """['|','|',('partner_id.ref_companies',
'in', [company_id]),('partner_id', '=', partner_id),('partner_id.child_ids',
'child_of', [partner_id])]""")

        res['arch'] = etree.tostring(doc)
        return res
