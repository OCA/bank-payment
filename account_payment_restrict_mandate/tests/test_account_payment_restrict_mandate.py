# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
from openerp.tests.common import TransactionCase


class TestAccountPaymentRestrictMandate(TransactionCase):
    def test_account_payment_restrict_mandate(self):
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': self.env.ref('base.res_partner_2').bank_ids
            .filtered(lambda x: x.state == 'iban').id,
            'max_amount_per_date': 600,
            'rrule': [
                {
                    'type': 'rrule',
                    'dtstart': time.strftime('%Y') + '-01-01 00:00:00',
                    'until': time.strftime('%Y') + '-03-02 00:00:00',
                    'freq': 1,
                    'interval': 1,
                    'bymonthday': [1],
                },
            ],
            'signature_date': time.strftime('%Y') + '-01-01',
        })
        self.assertEqual(mandate.max_amount, 1800)
        mandate.validate()
        payment_order = self.env['payment.order'].create({
            'reference': 'test',
            'date_prefered': 'fixed',
            'date_scheduled': time.strftime('%Y') + '-01-01',
            'mode': self.env.ref('account_payment.payment_mode_1').id,
            'payment_order_type': 'debit',
        })
        move_lines = (
            self.env.ref('account.invoice_3').move_id.line_id.filtered(
                lambda x: x.debit > 0) +
            self.env.ref('account.invoice_4').move_id.line_id.filtered(
                lambda x: x.debit > 0)
        )
        move_lines.mapped('invoice').write({
            'mandate_id': mandate.id,
        })
        self.env['payment.order.create'].with_context(
            active_id=payment_order.id,
            active_model='payment.order',
            search_payment_order_type='debit',
        ).create({
            'entries': [(6, 0, move_lines.ids)],
        }).create_payment()
        self.assertEqual(payment_order.total, 600)
