# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class TestMandate(TransactionCase):

    def test_mandate_01(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
            })
        self.assertEqual(mandate.state, 'draft')
        mandate.validate()
        self.assertEqual(mandate.state, 'valid')
        mandate.cancel()
        self.assertEqual(mandate.state, 'cancel')
        mandate.back2draft()
        self.assertEqual(mandate.state, 'draft')

    def test_mandate_02(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
            })
        with self.assertRaises(UserError):
            mandate.back2draft()

    def test_mandate_03(self):
        bank_account = self.env.ref(
            'account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        mandate.validate()

        with self.assertRaises(UserError):
            mandate.validate()

    def test_mandate_04(self):
        bank_account = self.env.ref(
            'account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        mandate.validate()
        mandate.cancel()
        with self.assertRaises(UserError):
            mandate.cancel()

    def test_onchange_methods(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].new({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        bank_account_2 = self.env.ref(
            'account_payment_mode.res_partner_2_iban')
        mandate.partner_bank_id = bank_account_2
        mandate.mandate_partner_bank_change()
        self.assertEquals(mandate.partner_id, bank_account_2.partner_id)

    def test_constrains_01(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        mandate.validate()
        with self.assertRaises(ValidationError):
            mandate.signature_date = fields.Date.to_string(
                fields.Date.from_string(
                    fields.Date.context_today(mandate)) + timedelta(days=1))

    def test_constrains_02(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })

        with self.assertRaises(ValidationError):
            mandate.company_id = self.company_2

    def test_constrains_03(self):
        bank_account = self.env.ref('account_payment_mode.res_partner_12_iban')
        mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_account.id,
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        bank_account_2 = self.env['res.partner.bank'].create({
            'acc_number': '1234',
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            mandate.partner_bank_id = bank_account_2

    def test_constrains_04(self):
        mandate = self.env['account.banking.mandate'].create({
            'signature_date': '2015-01-01',
            'company_id': self.company.id,
        })
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '1234',
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            bank_account.mandate_ids += mandate

    def setUp(self):
        res = super(TestMandate, self).setUp()
        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })
        return res
