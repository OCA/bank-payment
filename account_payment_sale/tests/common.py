# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class CommonTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.bank = cls.env["res.partner.bank"].create(
            {"acc_number": "test", "partner_id": cls.env.user.company_id.partner_id.id}
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "test journal",
                "code": "123",
                "type": "bank",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_id": cls.bank.id,
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "test_mode",
                "active": True,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
            }
        )
        cls.payment_mode_2 = cls.env["account.payment.mode"].create(
            {
                "name": "test_mode_2",
                "active": True,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.journal.id,
            }
        )
        cls.base_partner = cls.env["res.partner"].create(
            {
                "name": "Dummy",
                "email": "dummy@example.com",
                "customer_payment_mode_id": cls.payment_mode.id,
            }
        )
        cls.products = {
            "prod_order": cls.env["product.product"].create(
                {
                    "name": "Test product order",
                    "detailed_type": "consu",
                    "list_price": 280,
                    "standard_price": 235,
                }
            ),
            "prod_del": cls.env["product.product"].create(
                {
                    "name": "Test product delivery",
                    "detailed_type": "consu",
                    "list_price": 70,
                    "standard_price": 55,
                }
            ),
            "serv_order": cls.env["product.product"].create(
                {
                    "name": "Test service product order",
                    "type": "service",
                    "invoice_policy": "order",
                }
            ),
            "serv_del": cls.env["product.product"].create(
                {
                    "name": "Test service product delivery",
                    "type": "service",
                    "invoice_policy": "delivery",
                }
            ),
        }
