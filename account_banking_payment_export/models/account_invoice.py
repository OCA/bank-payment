# -*- coding: utf-8 -*-
# © 2013-2014 ACSONE SA (<http://acsone.eu>).
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _
from lxml import etree


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_reference_type(self):
        rt = super(AccountInvoice, self)._get_reference_type()
        rt.append(('structured', _('Structured Reference')))
        return rt

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False,
                        submenu=False):
        """This adds the field 'reference_type' only if the view doesn't
        contain this field (this is for customer invoice and with
        l10n_be_invoice_bba not installed).
        """
        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'form':
            return res
        field_name = 'reference_type'
        doc = etree.XML(res['arch'])
        if not doc.xpath("//field[@name='%s']" % field_name):
            nodes = doc.xpath("//field[@name='origin']")
            if nodes:
                field = self.fields_get([field_name])[field_name]
                field_xml = etree.Element(
                    'field', {'name': field_name,
                              'widget': 'selection',
                              'states': str(field['states']),
                              'selection': str(field['selection']),
                              'required': '1' if field['required'] else '0',
                              'string': field['string'],
                              'nolabel': '0'})
                nodes[0].addnext(field_xml)
                res['arch'] = etree.tostring(doc)
                res['fields'][field_name] = field
        return res
