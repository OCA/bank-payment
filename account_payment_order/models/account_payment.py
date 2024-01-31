# Copyright 2019 ACSONE SA/NV
# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2024 FactorLibre - Aritz Olea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_order_id = fields.Many2one(comodel_name="account.payment.order")
    payment_line_ids = fields.Many2many(comodel_name="account.payment.line")

    @api.depends("payment_type", "journal_id")
    def _compute_payment_method_line_fields(self):
        res = super()._compute_payment_method_line_fields()
        for pay in self:
            if pay.payment_order_id:
                pay.available_payment_method_line_ids = (
                    pay.journal_id._get_available_payment_method_lines(pay.payment_type)
                )
            else:
                pay.available_payment_method_line_ids = (
                    pay.journal_id._get_available_payment_method_lines(
                        pay.payment_type
                    ).filtered(lambda x: not x.payment_method_id.payment_order_only)
                )
            to_exclude = pay._get_payment_method_codes_to_exclude()
            if to_exclude:
                pay.available_payment_method_line_ids = (
                    pay.available_payment_method_line_ids.filtered(
                        lambda x: x.code not in to_exclude
                    )
                )
        return res

    def _compute_available_partner_bank_ids(self):
        """Overrides available_partner_bank_ids compute method for payments which
        belong to a payment order. Without this override, in case compute method is
        triggered, these payments' bank value is replaced by an incorrect value."""
        order_pays = self.filtered(lambda p: p.payment_order_id and p.payment_line_ids)
        for pay in order_pays:
            pay.available_partner_bank_ids = pay.payment_line_ids[0].partner_bank_id
        return super(
            AccountPayment, self - order_pays
        )._compute_available_partner_bank_ids()
