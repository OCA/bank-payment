# Copyright 2014-16 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_mode_filter_type_domain = fields.Char(
        compute="_compute_payment_mode_filter_type_domain"
    )
    partner_bank_filter_type_domain = fields.Many2one(
        comodel_name="res.partner", compute="_compute_partner_bank_filter_type_domain"
    )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        compute="_compute_payment_mode",
        store=True,
        ondelete="restrict",
        readonly=False,
        check_company=True,
        tracking=True,
    )
    bank_account_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.bank_account_required", readonly=True
    )
    partner_bank_id = fields.Many2one(
        compute="_compute_partner_bank",
        store=True,
        ondelete="restrict",
        readonly=False,
    )
    has_reconciled_items = fields.Boolean(
        help="Technical field for supporting the editability of the payment mode",
        compute="_compute_has_reconciled_items",
    )

    @api.depends("move_type")
    def _compute_payment_mode_filter_type_domain(self):
        for move in self:
            if move.move_type in ("out_invoice", "in_refund"):
                move.payment_mode_filter_type_domain = "inbound"
            elif move.move_type in ("in_invoice", "out_refund"):
                move.payment_mode_filter_type_domain = "outbound"
            else:
                move.payment_mode_filter_type_domain = False

    @api.depends("partner_id", "move_type")
    def _compute_partner_bank_filter_type_domain(self):
        for move in self:
            if move.move_type in ("out_invoice", "in_refund"):
                move.partner_bank_filter_type_domain = move.bank_partner_id
            elif move.move_type in ("in_invoice", "out_refund"):
                move.partner_bank_filter_type_domain = move.commercial_partner_id
            else:
                move.partner_bank_filter_type_domain = False

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode(self):
        for move in self:
            move.payment_mode_id = move.payment_mode_id
            if move.company_id and move.payment_mode_id.company_id != move.company_id:
                move.payment_mode_id = False
            if move.partner_id:
                partner = move.with_company(move.company_id.id).partner_id
                if move.move_type == "in_invoice":
                    move.payment_mode_id = partner.supplier_payment_mode_id
                elif move.move_type == "out_invoice":
                    move.payment_mode_id = partner.customer_payment_mode_id
                elif (
                    move.move_type in ["out_refund", "in_refund"]
                    and move.reversed_entry_id
                ):
                    move.payment_mode_id = (
                        move.reversed_entry_id.payment_mode_id.refund_payment_mode_id
                    )
                elif not move.reversed_entry_id:
                    if move.move_type == "out_refund":
                        move.payment_mode_id = (
                            partner.customer_payment_mode_id.refund_payment_mode_id
                        )
                    elif move.move_type == "in_refund":
                        move.payment_mode_id = (
                            partner.supplier_payment_mode_id.refund_payment_mode_id
                        )

    @api.depends("line_ids.matched_credit_ids", "line_ids.matched_debit_ids")
    def _compute_has_reconciled_items(self):
        for record in self:
            lines_to_consider = record.line_ids.filtered(
                lambda x: x.account_id.internal_type in ("receivable", "payable")
            )
            record.has_reconciled_items = bool(
                lines_to_consider.matched_credit_ids
                + lines_to_consider.matched_debit_ids
            )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """Force compute because the onchange chain doesn't call
        ``_compute_partner_bank``.
        """
        res = super()._onchange_partner_id()
        self._compute_partner_bank()
        return res

    @api.depends("partner_id", "payment_mode_id")
    def _compute_partner_bank(self):
        for move in self:
            # No bank account assignation is done for out_invoice as this is only
            # needed for printing purposes and it can conflict with
            # SEPA direct debit payments. Current report prints it.
            def get_bank_id():
                return move.commercial_partner_id.bank_ids.filtered(
                    lambda b: b.company_id == move.company_id or not b.company_id
                )[:1]

            bank_id = False
            if move.partner_id:
                pay_mode = move.payment_mode_id
                if move.move_type == "in_invoice":
                    if (
                        pay_mode
                        and pay_mode.payment_type == "outbound"
                        and pay_mode.payment_method_id.bank_account_required
                        and move.commercial_partner_id.bank_ids
                    ):
                        bank_id = get_bank_id()
            move.partner_bank_id = bank_id

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super()._reverse_move_vals(default_values, cancel=cancel)
        move_vals["payment_mode_id"] = self.payment_mode_id.refund_payment_mode_id.id
        if self.move_type == "in_invoice":
            move_vals["partner_bank_id"] = self.partner_bank_id.id
        return move_vals

    def partner_banks_to_show(self):
        self.ensure_one()
        if self.partner_bank_id:
            return self.partner_bank_id
        return self.payment_mode_id.partner_banks_to_show()

    @api.model
    def create(self, vals):
        """Force compute partner_bank_id when invoice is created from SO
        to avoid that odoo _prepare_invoice method value will be set.
        """
        if self.env.context.get("active_model") == "sale.order":  # pragma: no cover
            virtual_move = self.new(vals)
            virtual_move._compute_partner_bank()
            vals["partner_bank_id"] = virtual_move.partner_bank_id.id
        return super().create(vals)
