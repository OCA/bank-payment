from odoo import api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def _get_allowed_move_types(self):
        return ["out_invoice", "in_invoice", "out_refund", "in_refund"]

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        if self._context.get("active_model") == "account.move":
            account_move_ids = self.env["account.move"].browse(
                self._context.get("active_ids", [])
            )
            if len(account_move_ids) == 1 and account_move_ids.payment_mode_id:
                if account_move_ids.move_type not in self._get_allowed_move_types():
                    return res
                if account_move_ids.payment_mode_id.bank_account_link == "fixed":
                    payment_mode_payment_type = (
                        account_move_ids.payment_mode_id.payment_type
                    )
                    payment_mode_journal_id = (
                        account_move_ids.payment_mode_id.fixed_journal_id
                    )
                    payment_mode_payment_method_id = (
                        account_move_ids.payment_mode_id.payment_method_id
                    )

                    res["journal_id"] = payment_mode_journal_id.id

                    payment_method_line_id = self.env[
                        "account.payment.method.line"
                    ].search(
                        [
                            ("journal_id", "=", payment_mode_journal_id.id),
                            (
                                "payment_method_id",
                                "=",
                                payment_mode_payment_method_id.id,
                            ),
                            ("payment_type", "=", payment_mode_payment_type),
                        ],
                        limit=1,
                    )
                    if payment_method_line_id:
                        res["payment_method_line_id"] = payment_method_line_id.id
                else:
                    payment_mode_payment_type = (
                        account_move_ids.payment_mode_id.payment_type
                    )
                    payment_mode_journal_ids = (
                        account_move_ids.payment_mode_id.variable_journal_ids
                    )
                    payment_mode_payment_method_id = (
                        account_move_ids.payment_mode_id.payment_method_id
                    )

                    res["journal_id"] = (
                        payment_mode_journal_ids and payment_mode_journal_ids[0].id
                    )
                    payment_method_line_id = self.env[
                        "account.payment.method.line"
                    ].search(
                        [
                            ("journal_id", "in", payment_mode_journal_ids.ids),
                            (
                                "payment_method_id",
                                "=",
                                payment_mode_payment_method_id.id,
                            ),
                            ("payment_type", "=", payment_mode_payment_type),
                        ]
                    )
                    if payment_method_line_id:
                        res["payment_method_line_id"] = (
                            payment_method_line_id and payment_method_line_id[0].id
                        )
        return res
