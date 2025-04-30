# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account_payment_order.tests.test_payment_order_inbound import (
    TestPaymentOrderInboundBase,
)
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestAccountPaymentOrder(TestPaymentOrderInboundBase):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test sequence pay",
                "code": "test.custom.sequence",
                "prefix": "",
                "suffix": ".xml",
                "padding": 2,
                "number_next": 1,
                "number_increment": 1,
                "company_id": False,
            }
        )

        cls.inbound_mode.write(
            {
                "filename_sequence_id": cls.sequence.id,
            }
        )

    def test_get_filename_with_sequence_filled(self):
        """
        Ensure the sequence is correctly used to generate the filename.
        """
        payment_order = self.inbound_order

        filename = payment_order._set_payment_filename("")
        expected_filename = "01.xml"  # As it's the first time we generate it
        self.assertEqual(expected_filename, filename)

    def test_get_filename_with_sequence_not_filled(self):
        """
        Ensure the original filename is kept when the sequence is not set
        """
        payment_order = self.inbound_order
        payment_order.payment_mode_id.write({"filename_sequence_id": False})
        expected_filename = "test.xml"

        filename = payment_order._set_payment_filename(expected_filename)

        self.assertEqual(expected_filename, filename)
