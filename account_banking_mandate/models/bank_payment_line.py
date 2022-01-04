# Copyright 2014-2022 Compassion CH - Cyril Sester <csester@compassion.ch>
# Copyright 2014-2022 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2015-2022 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BankPaymentLine(models.Model):
    _inherit = "bank.payment.line"

    mandate_id = fields.Many2one(
        comodel_name="account.banking.mandate",
        string="Direct Debit Mandate",
        related="payment_line_ids.mandate_id",
        check_company=True,
    )

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        res = super().same_fields_payment_line_and_bank_payment_line()
        res.append("mandate_id")
        return res
