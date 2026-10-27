# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class AccountBankingMandateCommon(BaseCommon):
    _test_user_groups = (
        "base.group_user",
        "base.group_partner_manager",
        "account.group_account_manager",
        "account_payment_order.group_account_payment",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company_2 = cls.env["res.company"].create({"name": "Company 2"})
        cls.company_2.partner_id.company_id = cls.company_2.id
        cls._test_user.company_ids |= cls.company_2

        cls.partner_bank = cls._create_partner_bank(
            cls.env,
            cls.partner,
            "FR66 1212 1212 1212 1212 1212 121",
            cls.company,
        )
        cls.mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.partner_bank.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )
        cls.alternative_bank_account = cls._create_partner_bank(
            cls.env,
            cls.partner,
            "FR66 2222 2222 2222 2222 2222 222",
            cls.company,
        )
        cls.alternative_mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.alternative_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company.id,
            }
        )
        cls.other_company_bank_account = cls._create_partner_bank(
            cls.env,
            cls.company_2.partner_id,
            "1234",
            cls.company_2,
        )
        cls.other_company_mandate = cls.env["account.banking.mandate"].create(
            {
                "partner_bank_id": cls.other_company_bank_account.id,
                "signature_date": "2015-01-01",
                "company_id": cls.company_2.id,
            }
        )
        cls.readonly_user = new_test_user(
            cls.env,
            name="Mandate Read Only User",
            login="mandate_read_only_user",
            email="mandate_read_only_user@test.com",
            group_ids=[cls.env.ref("base.group_user").id],
            company_id=cls.company.id,
            company_ids=[cls.company.id],
        )

    @classmethod
    def _create_partner_bank(
        cls,
        env: api.Environment,
        partner: models.Model,
        account_number: str,
        company: models.Model | None = None,
    ) -> models.Model:
        return env["res.partner.bank"].create(
            {
                "account_number": account_number,
                "bank_name": "Test Bank",
                "bank_bic": "TESTBICXXXX",
                "partner_id": partner.id,
                "company_id": company.id if company else False,
            }
        )
