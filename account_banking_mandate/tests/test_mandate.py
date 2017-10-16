# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMandate(TransactionCase):

    def test_mandate(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            })
        self.assertEqual(mandate.state, 'draft')
        mandate.validate()
        self.assertEqual(mandate.state, 'valid')
        self.assertEqual(bank_account.partner_id.mandate_count, 1)
        mandate.cancel()
        self.assertEqual(mandate.state, 'cancel')
        mandate.back2draft()
        self.assertEqual(mandate.state, 'draft')
