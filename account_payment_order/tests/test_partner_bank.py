import unittest
from odoo.tests.common import TransactionCase

class TestPartnerBank(TransactionCase):

    def setUp(self):
        super(TestPartnerBank, self).setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })

        self.bank_allowed = self.env['res.partner.bank'].create({
            'acc_number': '1234567890',
            'partner_id': self.partner.id,
            'allow_out_payment': True,
        })
        self.bank_not_allowed = self.env['res.partner.bank'].create({
            'acc_number': '0987654321',
            'partner_id': self.partner.id,
            'allow_out_payment': False,
        })

    def test_partner_bank_domain(self):

        payment = self.env['account.payment'].create({
            'partner_id': self.partner.id,
            'payment_type': 'outbound',
        })

        domain = payment.fields_get()['partner_bank_id']['domain']
        bank_ids = self.env['res.partner.bank'].search(domain)
        self.assertIn(self.bank_allowed, bank_ids)
        self.assertNotIn(self.bank_not_allowed, bank_ids)

if __name__ == '__main__':
    unittest.main()
