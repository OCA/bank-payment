# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestMandate(TransactionCase):
    def test_contrains(self):
        with self.assertRaises(ValidationError):
            self.mandate.recurrent_sequence_type = False
            self.mandate.type = 'recurrent'
            self.mandate._check_recurring_type()

    def test_onchange_bank(self):
        self.mandate.write({
            'type': 'recurrent', 'recurrent_sequence_type': 'recurring'
        })
        self.mandate.validate()
        self.mandate.partner_bank_id = self.env.ref(
            'account_payment_mode.res_partner_2_iban'
        )
        self.mandate.mandate_partner_bank_change()
        self.assertEqual(self.mandate.recurrent_sequence_type, 'first')

    def test_expire(self):
        self.mandate.signature_date = datetime.now() + relativedelta(
            months=-50)
        self.mandate.validate()
        self.assertEqual(self.mandate.state, 'valid')
        self.env['account.banking.mandate']._sdd_mandate_set_state_to_expired()
        self.assertEqual(self.mandate.state, 'expired')

    def setUp(self):
        res = super(TestMandate, self).setUp()
        self.partner = self.env.ref('base.res_partner_12')
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        self.mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'format': 'sepa',
            'type': 'oneoff',
            'signature_date': '2015-01-01',
        })
        return res
