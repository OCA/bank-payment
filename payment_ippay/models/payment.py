# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('ippay', 'IPpay')])
    api_url = fields.Char("Api URL")
    ippay_terminal_id = fields.Char("IPpay TerminalID")


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    @api.model
    def ippay_create(self, values):
        acquirer = self.env['payment.acquirer'].browse(
            values['acquirer_id'])
        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            card_detail = {'cc_number': values['cc_number'],
                           'expiry_month': values['cc_expiry_month'],
                           'expiry_year': values['cc_expiry_year']}

            xml = '''<ippay>
            <TransactionType>TOKENIZE</TransactionType>
            <TerminalID>%s</TerminalID>
            <CardNum>%s</CardNum>
            <CardExpMonth>%s</CardExpMonth>
            <CardExpYear>%s</CardExpYear>
            </ippay>''' % (acquirer.ippay_terminal_id,
                           card_detail.get('cc_number'),
                           card_detail.get('expiry_month'),
                           card_detail.get('expiry_year'))
            if acquirer.api_url:
                url = acquirer.api_url
            r = requests.post(url,
                              data=xml, headers={'Content-Type': 'text/xml'})
            data = xmltodict.parse(
                r.content)
            token = data['IPPayResponse'].get('Token')
            if token:
                return {
                    'name': 'XXXXXXXXXXXX%s - %s' % (
                        values['cc_number'][-4:], values['cc_holder_name']),
                    'acquirer_ref': token,
                }
            else:
                raise ValidationError(
                    _('Customer payment token creation in IPpay failed: %s' % (
                        data['IPPayResponse'].get('ErrMsg'))
                      ))
        else:
            return values
