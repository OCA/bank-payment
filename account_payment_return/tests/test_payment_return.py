from openerp.tests.common import TransactionCase

class TestPaymentReturn(TransactionCase):
    """Tests for payment returns

    Test used to check that when doing a payment return the result will be balanced.
    """

    def setUp(self):
        a = 3
        super(TestPaymentReturn, self).setUp()
        self.account_invoice_model = self.registry('account.invoice')

    def test_balanced_customer_invoice(self):
        cr, uid = self.cr, self.uid
