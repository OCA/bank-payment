# Copyright 2014-16 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    )
    bank_account_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.bank_account_required", readonly=True
    )
    invoice_partner_bank_id = fields.Many2one(
        compute="_compute_invoice_partner_bank",
        store=True,
        ondelete="restrict",
        readonly=False,
    )

    @api.depends("type")
    def _compute_payment_mode_filter_type_domain(self):
        for move in self:
            if move.type in ("out_invoice", "in_refund"):
                move.payment_mode_filter_type_domain = "inbound"
            elif move.type in ("in_invoice", "out_refund"):
                move.payment_mode_filter_type_domain = "outbound"
            else:
                move.payment_mode_filter_type_domain = False

    @api.depends("partner_id", "type")
    def _compute_partner_bank_filter_type_domain(self):
        for move in self:
            if move.type in ("out_invoice", "in_refund"):
                move.partner_bank_filter_type_domain = move.bank_partner_id
            elif move.type in ("in_invoice", "out_refund"):
                move.partner_bank_filter_type_domain = move.commercial_partner_id
            else:
                move.partner_bank_filter_type_domain = False

    @api.depends("partner_id", "company_id")
    def _compute_payment_mode(self):
        for move in self:
            move.payment_mode_id = False
            if move.partner_id:
                partner = move.with_context(force_company=move.company_id.id).partner_id
                if move.type == "in_invoice":
                    move.payment_mode_id = partner.supplier_payment_mode_id
                elif move.type == "out_invoice":
                    move.payment_mode_id = partner.customer_payment_mode_id
                elif (
                    move.type in ["out_refund", "in_refund"] and move.reversed_entry_id
                ):
                    move.payment_mode_id = (
                        move.reversed_entry_id.payment_mode_id.refund_payment_mode_id
                    )
                elif not move.reversed_entry_id:
                    if move.type == "out_refund":
                        move.payment_mode_id = (
                            partner.customer_payment_mode_id.refund_payment_mode_id
                        )
                    elif move.type == "in_refund":
                        move.payment_mode_id = (
                            partner.supplier_payment_mode_id.refund_payment_mode_id
                        )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """Force compute because the onchange chain doesn't call
        ``_compute_invoice_partner_bank``.
        """
        res = super()._onchange_partner_id()
        self._compute_invoice_partner_bank()
        return res

    @api.depends("partner_id", "payment_mode_id")
    def _compute_invoice_partner_bank(self):
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
                if move.type == "in_invoice":
                    if (
                        pay_mode
                        and pay_mode.payment_type == "outbound"
                        and pay_mode.payment_method_id.bank_account_required
                        and move.commercial_partner_id.bank_ids
                    ):
                        bank_id = get_bank_id()
            move.invoice_partner_bank_id = bank_id

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super()._reverse_move_vals(default_values, cancel=cancel)
        move_vals["payment_mode_id"] = self.payment_mode_id.refund_payment_mode_id.id
        if self.type == "in_invoice":
            move_vals["invoice_partner_bank_id"] = self.invoice_partner_bank_id.id
        return move_vals

    @api.constrains("company_id", "payment_mode_id")
    def _check_payment_mode_company_constrains(self):
        for rec in self.sudo():
            if rec.payment_mode_id and rec.company_id != rec.payment_mode_id.company_id:
                raise ValidationError(
                    _(
                        "The company of the invoice %s does not match "
                        "with that of the payment mode"
                    )
                    % rec.name
                )

    def partner_banks_to_show(self):
        self.ensure_one()
        if self.invoice_partner_bank_id:
            return self.invoice_partner_bank_id
        if self.payment_mode_id.show_bank_account_from_journal:
            if self.payment_mode_id.bank_account_link == "fixed":
                return self.payment_mode_id.fixed_journal_id.bank_account_id
            else:
                return self.payment_mode_id.variable_journal_ids.mapped(
                    "bank_account_id"
                )
        if (
            self.payment_mode_id.payment_method_id.code == "sepa_direct_debit"
        ):  # pragma: no cover
            return (
                self.mandate_id.partner_bank_id
                or self.partner_id.valid_mandate_id.partner_bank_id
            )
        # Return this as empty recordset
        return self.invoice_partner_bank_id

    @api.model
    def create(self, vals):
        """ Force compute invoice_partner_bank_id when invoice is created from SO
         to avoid that odoo _prepare_invoice method value will be set"""
        if self.env.context.get("active_model") == "sale.order":  # pragma: no cover
            virtual_move = self.new(vals)
            virtual_move._compute_invoice_partner_bank()
            vals["invoice_partner_bank_id"] = virtual_move.invoice_partner_bank_id
        return super().create(vals)
