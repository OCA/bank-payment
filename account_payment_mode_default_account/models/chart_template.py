# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _get_property_accounts(self, additional_properties):
        property_accounts = super()._get_property_accounts(additional_properties)
        property_accounts["property_stored_account_receivable_id"] = "res.partner"
        property_accounts["property_stored_account_payable_id"] = "res.partner"
        return property_accounts
