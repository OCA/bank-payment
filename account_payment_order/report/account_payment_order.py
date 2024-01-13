# © 2017 Acsone SA/NV (<https://www.acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.misc import formatLang


class AccountPaymentOrderReport(models.AbstractModel):
    _name = "report.account_payment_order.print_account_payment_order_main"
    _description = "Technical model for printing payment order"

    @api.model
    def _get_report_values(self, docids, data=None):
        AccountPaymentOrderObj = self.env["account.payment.order"]
        docs = AccountPaymentOrderObj.browse(docids)

        return {
            "doc_ids": docids,
            "doc_model": "account.payment.order",
            "docs": docs,
            "data": data,
            "env": self.env,
            "get_bank_account_name": self.get_bank_account_name,
            "formatLang": formatLang,
        }

    @api.model
    def get_bank_account_name(self, partner_bank):
        """

        :param partner_bank:
        :return:
        """
        if partner_bank:
            name = ""
            if partner_bank.bank_name:
                name = "%s: " % partner_bank.bank_id.name
            if partner_bank.acc_number:
                name = f"{name} {partner_bank.acc_number}"
                if partner_bank.bank_bic:
                    name = "%s - " % (name)
            if partner_bank.bank_bic:
                name = f"{name} BIC {partner_bank.bank_bic}"
            return name
        else:
            return False
