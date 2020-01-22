# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
import xmltodict
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTansaction(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def _ippay_s2s_do_payment(self, invoice):
        acquirer = self.acquirer_id
        request = '''
            <ippay>
                <TransactionType>SALE</TransactionType>
                <TerminalID>%s</TerminalID>
                <Token>%s</Token>
                <TotalAmount>%s</TotalAmount>
            </ippay>''' % (
                acquirer.ippay_terminal_id,
                self.payment_token_id.acquirer_ref,
                str(self.amount).replace('.', ''))
        # TODO_ add verbosity parameter?
        _logger.info("Request to get IPPay Transaction ID: %s" % (request))
        try:
            r = requests.post(
                acquirer.api_url,
                data=request,
                headers={'Content-Type': 'text/xml'})
        except Exception as e:
            raise ValidationError(_(e))
        _logger.info("Transaction Received: %s" % (r.content))

        data = xmltodict.parse(r.content)
        response = data.get('ippayResponse')
        # TODO: don't set as really paid if using test environment
        # - risk of wrong data in Production db!
        if response.get('ResponseText') == 'APPROVED':
            self.acquirer_reference = response.get(
                'TransactionID')
            self.date = fields.Datetime.now()
            self.state = 'done'
        else:
            self.state = 'cancel'
            invoice.message_post(
                body=_("IPPay Credit Card Payment DECLINED: %s - %s") % (
                    response.get('ActionCode'),
                    response.get('ErrMsg'),
                ))

    @api.multi
    def ippay_s2s_do_transaction(self):
        context = self.env.context
        inv_rec = self.env['account.invoice'].browse(context.get('active_ids'))
        for inv in inv_rec:
            if inv.type == 'out_invoice':
                self._ippay_s2s_do_payment(invoice=inv)
