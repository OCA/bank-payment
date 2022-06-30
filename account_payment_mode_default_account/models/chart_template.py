# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def generate_properties(self, acc_template_ref, company):
        super().generate_properties(acc_template_ref, company)
        # Make sure a property with stored in its name is created as default for the company
        # so that _get_multi would fetch it if the partner does not have a property itself
        PropertyObj = self.env["ir.property"]
        todo_list = [
            (
                "property_account_receivable_id",
                "property_stored_account_receivable_id",
                "res.partner",
            ),
            (
                "property_account_payable_id",
                "property_stored_account_payable_id",
                "res.partner",
            ),
        ]
        for chart_field, partner_field, model in todo_list:
            account = self[chart_field]
            value = acc_template_ref[account.id] if account else False
            if value:
                PropertyObj._set_default(partner_field, model, value, company=company)
