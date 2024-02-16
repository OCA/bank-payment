# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from datetime import date
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestAccountPaymentMethodFsStorage(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.company_data["company"]

        cls.fs_storage = cls.env.ref("fs_storage.default_fs_storage")

        cls.fs_storage.write(
            {
                "use_on_payment_method": True,
            }
        )
        cls.payment_method = cls.env.ref(
            "account.account_payment_method_manual_out"
        ).copy(
            {
                "storage": str(cls.fs_storage.id),
                "name": "method test",
                "code": "test",
            }
        )

        cls.creation_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test Direct Debit of suppliers from Société Générale",
                "company_id": cls.company.id,
                "bank_account_link": "variable",
                "payment_method_id": cls.payment_method.id,
            }
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        # create payment order with payment method and fs storage

    @contextmanager
    def with_custom_method(self):
        path = (
            "odoo.addons.account_payment_order.models"
            ".account_payment_order.AccountPaymentOrder.generate_payment_file"
        )
        with patch(
            path,
            new=lambda self: (b"Content", "Filename"),
            create=not hasattr(
                self.env["account.payment.order"], "generate_payment_file"
            ),
        ):
            yield

    def test_payment_method_fs_storage(self):
        order_vals = {
            "payment_type": "outbound",
            "payment_mode_id": self.creation_mode.id,
            "journal_id": self.bank_journal.id,
        }

        order = self.env["account.payment.order"].create(order_vals)

        vals = {
            "order_id": order.id,
            "partner_id": self.partner.id,
            "communication": "manual line and manual date",
            "currency_id": order.payment_mode_id.company_id.currency_id.id,
            "amount_currency": 200,
            "date": date.today(),
        }
        self.env["account.payment.line"].create(vals)

        order.draft2open()
        with self.with_custom_method():
            action = order.open2generated()

        self.assertDictEqual(
            action,
            {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": "Generate and export",
                    "message": "The file has been generated and dropped on the storage.",
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            },
        )

        attachment = self.env["ir.attachment"].search(
            [("res_model", "=", "account.payment.order"), ("res_id", "=", order.id)]
        )

        self.assertEqual(len(attachment), 1)

    def test_check_use_on_payment_method(self):
        self.assertEqual(self.payment_method.storage, str(self.fs_storage.id))

        with self.assertRaisesRegex(
            UserError, "Storage is already used on at least one payment method"
        ):
            self.fs_storage.write({"use_on_payment_method": False})

        self.payment_method.write({"storage": False})
        self.fs_storage.write({"use_on_payment_method": False})

        self.assertFalse(self.payment_method.storage)
        self.assertFalse(self.fs_storage.use_on_payment_method)
