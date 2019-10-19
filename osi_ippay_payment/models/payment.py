# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
import json

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('ippay', 'IPpay')])


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    @api.model
    def ippay_create(self, values):

        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            card_detail = {'cc_number': values['cc_number'],
                           'expiry_month': values['cc_expiry_month'],
                           'expiry_year': values['cc_expiry_year']}

            xml = '''<ippay>
            <TransactionType>TOKENIZE</TransactionType>
            <TerminalID>TESTTERMINAL</TerminalID>
            <CardNum>%s</CardNum>
            <CardExpMonth>%s</CardExpMonth>
            <CardExpYear>%s</CardExpYear>
            </ippay>''' % (card_detail.get('cc_number'),
                           card_detail.get('expiry_month'),
                           card_detail.get('expiry_year'))

            r = requests.post('https://testgtwy.ippay.com/ippay',
                              data=xml, headers={'Content-Type': 'text/xml'})
            data = eval(json.dumps(xmltodict.parse(
                r.content)).replace('null', 'False'))
            token = data['IPPayResponse'].get('Token')
            if token:
                return {
                    'name': 'XXXXXXXXXXXX%s - %s' % (
                        values['cc_number'][-4:], values['cc_holder_name']),
                    'acquirer_ref': token,
                }
            else:
                raise ValidationError(
                    _('The Customer Profile creation in IPpay failed.'
                      ))
        else:
            return values
