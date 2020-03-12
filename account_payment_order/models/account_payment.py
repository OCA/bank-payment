# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _compute_journal_domain_and_types(self):
        res = super(AccountPayment, self)._compute_journal_domain_and_types()
        journal_domain = res.get("domain", [])
        if self.payment_type == "inbound":
            journal_domain.append(("inbound_payment_order_only", "=", False))
        else:
            journal_domain.append(("outbound_payment_order_only", "=", False))
        res["domain"] = journal_domain
        return res

    @api.onchange("journal_id")
    def _onchange_journal(self):
        res = super(AccountPayment, self)._onchange_journal()
        domains = res.get("domain")
        if not domains:
            return res
        if domains.get("payment_method_id"):
            domains["payment_method_id"].append(("payment_order_only", "!=", True))
        return res
