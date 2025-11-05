# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    grouped_move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="grouped_payment_order_id",
        string="Journal Entries (Grouped)",
        readonly=True,
    )
    grouped_move_count = fields.Integer(
        compute="_compute_grouped_move_count",
        string="Number of Grouped Journal Entries",
    )

    @api.depends("grouped_move_ids")
    def _compute_grouped_move_count(self):
        rg_res = self.env["account.move"].read_group(
            [("grouped_payment_order_id", "in", self.ids)],
            ["grouped_payment_order_id"],
            ["grouped_payment_order_id"],
        )
        mapped_data = {
            x["grouped_payment_order_id"][0]: x["grouped_payment_order_id_count"]
            for x in rg_res
        }
        for order in self:
            order.grouped_move_count = mapped_data.get(order.id, 0)

    def action_uploaded_cancel(self):
        """Unreconcile and remove grouped moves."""
        for move in self.grouped_move_ids:
            move.button_cancel()
            for move_line in move.line_ids:
                move_line.remove_move_reconcile()
            move.with_context(force_delete=True).unlink()
        return super().action_uploaded_cancel()

    def generated2uploaded(self):
        """Generate grouped moves if configured that way."""
        res = super().generated2uploaded()
        for order in self:
            if order.payment_mode_id.generate_move and len(order.payment_ids) > 1:
                order.generate_move()
        return res

    def generate_move(self):
        """Create the moves that pay off the move lines from the payment/debit order."""
        self.ensure_one()
        trfmoves = self._prepare_trf_moves()
        for hashcode, plines in trfmoves.items():
            self._create_reconcile_move(hashcode, plines)

    def _prepare_trf_moves(self):
        """Prepare a dict "trfmoves" grouped by date."""
        self.ensure_one()
        trfmoves = {}
        for pline in self.payment_ids:
            hashcode = fields.Date.to_string(pline.date)
            trfmoves.setdefault(hashcode, self.env["account.payment"])
            trfmoves[hashcode] += pline
        return trfmoves

    def _create_reconcile_move(self, hashcode, payments):
        self.ensure_one()
        post_move = self.payment_mode_id.post_move
        am_obj = self.env["account.move"]
        mvals = self._prepare_move(payments)
        move = am_obj.create(mvals)
        if post_move:
            move.action_post()
        self.reconcile_grouped_payments(move, payments)

    def reconcile_grouped_payments(self, move, payments):
        lines_to_rec = move.line_ids[:-1]
        for payment in payments:
            journal = payment.journal_id
            lines_to_rec += payment.move_id.line_ids.filtered(
                lambda x, journal=journal: x.account_id
                in (
                    journal._get_journal_inbound_outstanding_payment_accounts()
                    + journal._get_journal_outbound_outstanding_payment_accounts()
                )
            )
        lines_to_rec.reconcile()

    def _prepare_move(self, payments=None):
        if self.payment_type == "outbound":
            ref = _("Payment order %s") % self.name
        else:
            ref = _("Debit order %s") % self.name
        if payments and len(payments) == 1:
            ref += " - " + payments.name
        vals = {
            "date": payments[0].date,
            "journal_id": self.journal_id.id,
            "ref": ref,
            "grouped_payment_order_id": self.id,
            "line_ids": [],
        }
        total_company_currency = total_payment_currency = 0
        for pline in payments:
            amount_company_currency = abs(pline.move_id.line_ids[0].balance)
            total_company_currency += amount_company_currency
            total_payment_currency += pline.amount
            partner_ml_vals = self._prepare_move_line_partner_account(pline)
            vals["line_ids"].append((0, 0, partner_ml_vals))
        trf_ml_vals = self._prepare_move_line_offsetting_account(
            total_company_currency, total_payment_currency, payments
        )
        vals["line_ids"].append((0, 0, trf_ml_vals))
        return vals

    def _get_grouped_output_liquidity_account(self, payment):
        domain = [
            ("journal_id", "=", self.journal_id.id),
            ("payment_method_id", "=", payment.payment_method_id.id),
            ("payment_type", "=", self.payment_type),
        ]
        apml = self.env["account.payment.method.line"].search(domain)
        if apml.payment_account_id:
            return apml.payment_account_id
        elif self.payment_type == "inbound":
            return payment.company_id.account_journal_payment_debit_account_id
        else:
            return payment.company_id.account_journal_payment_credit_account_id

    def _prepare_move_line_partner_account(self, payment):
        if self.payment_type == "outbound":
            name = _("Payment bank line %s") % payment.name
        else:
            name = _("Debit bank line %s") % payment.name
        account = self._get_grouped_output_liquidity_account(payment)
        sign = self.payment_type == "inbound" and -1 or 1
        amount_company_currency = abs(payment.move_id.line_ids[0].balance)
        vals = {
            "name": name,
            "partner_id": payment.partner_id.id,
            "account_id": account.id,
            "credit": (
                self.payment_type == "inbound" and amount_company_currency or 0.0
            ),
            "debit": (
                self.payment_type == "outbound" and amount_company_currency or 0.0
            ),
            "currency_id": payment.currency_id.id,
            "amount_currency": payment.amount * sign,
            # Same logic as the individual payments
            "date_maturity": payment.payment_line_ids[0].date,
        }
        return vals

    def _prepare_move_line_offsetting_account(
        self, amount_company_currency, amount_payment_currency, payments
    ):
        if self.payment_type == "outbound":
            name = _("Payment order %s") % self.name
        else:
            name = _("Debit order %s") % self.name
        partner = self.env["res.partner"]
        for index, payment in enumerate(payments):
            account = self._get_grouped_output_liquidity_account(payment)
            if index == 0:
                partner = payment.payment_line_ids[0].partner_id
            elif payment.payment_line_ids[0].partner_id != partner:
                # we have different partners in the grouped move
                partner = self.env["res.partner"]
                break
        sign = self.payment_type == "outbound" and -1 or 1
        vals = {
            "name": name,
            "partner_id": partner.id,
            "account_id": account.id,
            "credit": (
                self.payment_type == "outbound" and amount_company_currency or 0.0
            ),
            "debit": (
                self.payment_type == "inbound" and amount_company_currency or 0.0
            ),
            "currency_id": payments[0].currency_id.id,
            "amount_currency": amount_payment_currency * sign,
            # All the lines should have the same date following _prepare_trf_moves
            "date_maturity": payments.payment_line_ids[:1].date,
        }
        return vals

    def action_grouped_moves(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_journal_line"
        )
        if self.grouped_move_count == 1:
            action.update(
                {
                    "view_mode": "form,list,kanban",
                    "views": False,
                    "view_id": False,
                    "res_id": self.grouped_move_ids.id,
                }
            )
        else:
            action["domain"] = [("id", "in", self.grouped_move_ids.ids)]
        ctx = self.env.context.copy()
        ctx.update({"search_default_misc_filter": 0})
        action["context"] = ctx
        return action
