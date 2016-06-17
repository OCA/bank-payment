# coding: utf-8
# © 2016 Opener B.V. - Stefan Rijnhart
from openerp.tests.common import TransactionCase


class TestAmendment(TransactionCase):

    def setUp(self):
        super(TestAmendment, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.mode = self.env.ref(
            'account_banking_sepa_direct_debit.sepa_direct_debit_mode')
        self.customer = self.env.ref('base.res_partner_12')
        self.mandate = self.env.ref(
            'account_banking_sepa_direct_debit.res_partner_12_mandate')
        self.old_bank = self.env.ref(
                    'account_banking_payment_export.res_partner_12_iban')
        self.new_bank = self.env.ref(
                    'account_banking_payment_export.res_partner_2_iban')

    def create_payment_order(self):
        payment = self.env['payment.order'].create({
            'mode': self.mode.id,
            'payment_order_type': self.mode.payment_order_type,
            'date_prefered': 'due',
            'mode_type': self.mode.type,
            'line_ids': [(0, 0, {
                'communication': '123',
                'amount_currency': 5.0,
                'partner_id': self.customer.id,
                'bank_id': self.mandate.partner_bank_id.id,
                'mandate_id': self.mandate.id,
            })],
        })
        payment.signal_workflow('open')
        export_wizard_model = payment.mode.type.ir_model_id.model
        export_wizard = self.env[export_wizard_model].with_context(
            active_ids=[payment.id]).create({})
        export_wizard.create_sepa()
        export_wizard.save_sepa()
        return payment

    def first_payment_and_write_bank_account(self):
        """ Create a debit order on the original bank account, then reset
        the bank account on the mandate and create another debit order """
        self.assertEqual(self.mandate.recurrent_sequence_type, 'first')
        self.create_payment_order()
        self.assertEqual(self.mandate.recurrent_sequence_type, 'recurring')
        self.mandate.write({'partner_bank_id': self.new_bank.id})
        self.assertEqual(self.mandate.recurrent_sequence_type, 'first')
        self.assertEqual(self.mandate.amendment_type, 'account')
        self.assertEqual(self.mandate.amendment_state, 'next')
        self.assertEqual(self.mandate.original_debtor_agent,
                         self.old_bank.bank_bic)
        self.create_payment_order()
        self.assertEqual(self.mandate.amendment_state, 'sent')
        self.assertEqual(self.mandate.recurrent_sequence_type, 'recurring')

    def test_01_further_debit_orders(self):
        """ Upon the second order on a mandate with an amendment, the amendment
        is cleared """
        self.first_payment_and_write_bank_account()
        self.create_payment_order()
        self.assertFalse(self.mandate.amendment_type)
        self.assertFalse(self.mandate.amendment_state)
        self.assertFalse(self.mandate.original_debtor_agent)

    def test_02_debit_rejected(self):
        """ When the first order on a mandate with an amendment is rejected,
        the mandate sequence type and the amendment state are reset. """
        self.first_payment_and_write_bank_account()
        self.mandate.amendment_reset()
        self.assertEqual(self.mandate.recurrent_sequence_type, 'first')
        self.assertEqual(self.mandate.amendment_type, 'account')
        self.assertEqual(self.mandate.amendment_state, 'next')
        self.assertEqual(self.mandate.original_debtor_agent,
                         self.old_bank.bank_bic)
