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
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        compute="_compute_payment_mode_id",
        store=True,
        precompute=True,
        ondelete="restrict",
        readonly=False,
        domain="[('payment_type', '=', payment_mode_filter_type_domain), "
        "('company_id', '=', company_id)]",
        check_company=True,
        tracking=True,
    )
    payment_method_code = fields.Char(
        related="payment_mode_id.payment_method_id.code", store=True
    )
    bank_account_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.bank_account_required", readonly=True
    )
    # partner_bank_id is defined in the 'account' module. It already has check_company=True
    # we just convert it to a computed field and add ondelete="restrict"
    partner_bank_id = fields.Many2one(
        compute="_compute_partner_bank_id",
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
            if move.is_inbound():  # out_invoice + in_refund
                move.payment_mode_filter_type_domain = "inbound"
            elif move.is_outbound():  # in_invoice + out_refund
                move.payment_mode_filter_type_domain = "outbound"
            else:
                move.payment_mode_filter_type_domain = False

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode_id(self):
        for move in self:
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

    @api.depends("bank_partner_id", "payment_mode_id")
    def _compute_partner_bank_id(self):
        res = super()._compute_partner_bank_id()
        for move in self:
            payment_mode = move.payment_mode_id
            if payment_mode:
                if (
                    move.move_type == "in_invoice"
                    and payment_mode.payment_type == "outbound"
                    and not payment_mode.payment_method_id.bank_account_required
                ):
                    move.partner_bank_id = False
                    continue
                elif move.move_type == "out_invoice":
                    if payment_mode.payment_method_id.bank_account_required:
                        if (
                            payment_mode.bank_account_link == "fixed"
                            and payment_mode.fixed_journal_id.bank_account_id
                        ):
                            move.partner_bank_id = (
                                payment_mode.fixed_journal_id.bank_account_id
                            )
                            continue
                    else:
                        move.partner_bank_id = False
            else:
                move.partner_bank_id = False
        return res

    @api.depends("line_ids.matched_credit_ids", "line_ids.matched_debit_ids")
    def _compute_has_reconciled_items(self):
        for record in self:
            lines_to_consider = record.line_ids.filtered(
                lambda x: x.account_id.account_type
                in ("asset_receivable", "liability_payable")
            )
            record.has_reconciled_items = bool(
                lines_to_consider.matched_credit_ids
                + lines_to_consider.matched_debit_ids
            )

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for _ in self]
        for move, default_values in zip(self, default_values_list):
            default_values[
                "payment_mode_id"
            ] = move.payment_mode_id.refund_payment_mode_id.id
            if move.move_type == "in_invoice":
                default_values["partner_bank_id"] = move.partner_bank_id.id
        return super()._reverse_moves(
            default_values_list=default_values_list, cancel=cancel
        )

    def partner_banks_to_show(self):
        self.ensure_one()
        if self.payment_mode_id:
            if (
                self.payment_mode_id.payment_method_id.code == "sepa_direct_debit"
            ):  # pragma: no cover
                return (
                    self.mandate_id.partner_bank_id
                    or self.partner_id.valid_mandate_id.partner_bank_id
                )
            if self.payment_mode_id.bank_account_link == "fixed":
                return self.payment_mode_id.fixed_journal_id.bank_account_id
            else:
                return self.payment_mode_id.variable_journal_ids.bank_account_id
        else:
            return self.company_id.partner_id.bank_ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Force compute partner_bank_id when invoice is created from SO
            # to avoid that odoo _prepare_invoice method value will be set.
            if self.env.context.get("active_model") == "sale.order":  # pragma: no cover
                virtual_move = self.new(vals)
                virtual_move._compute_partner_bank_id()
                vals["partner_bank_id"] = virtual_move.partner_bank_id.id
        return super().create(vals_list)
