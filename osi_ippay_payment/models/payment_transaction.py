# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
import json
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTansaction(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def _ippay_s2s_do_payment(self, invoice):
        amount = str(self.amount).replace('.', '')
        token_data = invoice.payment_token_id.acquirer_ref
        request = '''
            <ippay>
                <TransactionType>SALE</TransactionType>
                <TerminalID>TESTTERMINAL</TerminalID>
                <Token>%s</Token>
                <TotalAmount>%s</TotalAmount>
            </ippay>''' % (token_data, int(amount))

        _logger.info("Request to get IPPay Transaction ID: %s" % (request))
        url = 'https://testgtwy.ippay.com/ippay'
        try:
            r = requests.post(url, data=request, headers={
                'Content-Type': 'text/xml'})
            data = eval(json.dumps(xmltodict.parse(r.content)
                                   ).replace('null', 'False'))
            _logger.info("Transaction Received: %s" % (r.content))
            if data['ippayResponse'].get('ResponseText') == 'APPROVED':
                self.acquirer_reference = data['ippayResponse'].get(
                    'TransactionID')
                self.date = fields.Datetime.now()
                self.state = 'done'
                if self.payment_id.state == 'draft':
                    self.payment_id.post()
            else:
                self.state = 'cancel'
                invoice.message_post(
                    body="IPPay Payment Confirmation Declined")

        except Exception as e:
            raise ValidationError(_(e))

    @api.multi
    def ippay_s2s_do_transaction(self):
        context = self.env.context
        inv_obj = self.env['account.invoice']
        if len(context.get('active_ids')) == 1:
            inv_rec = inv_obj.search(
                [('id', '=', context.get('active_id')),
                 ('type', '=', 'out_invoice')])
            self._ippay_s2s_do_payment(invoice=inv_rec)
        if len(context.get('active_ids')) > 1:
            if context['active_domain'][0][2] == 'out_invoice':
                inv_rec = inv_obj.search(
                    [('id', 'in', context.get('active_ids')),
                     ('type', '=', 'out_invoice')])
                for rec in inv_rec:
                    self._ippay_s2s_do_payment(invoice=rec)
