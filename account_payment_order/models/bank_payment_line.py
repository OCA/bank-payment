# Copyright 2015-2016 Akretion - Alexis de Lattre
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BankPaymentLine(models.Model):
    _name = "bank.payment.line"
    _description = "Bank Payment Lines"
    _check_company_auto = True

    name = fields.Char(string="Bank Payment Line Ref", required=True, readonly=True)
    order_id = fields.Many2one(
        comodel_name="account.payment.order",
        ondelete="cascade",
        index=True,
        readonly=True,
        check_company=True,
    )
    payment_type = fields.Selection(
        related="order_id.payment_type", readonly=True, store=True
    )
    state = fields.Selection(related="order_id.state", readonly=True, store=True)
    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="bank_line_id",
        string="Payment Lines",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="payment_line_ids.partner_id",
        readonly=True,
        store=True,
        check_company=True,
    )  # store=True for groupby
    # Function Float fields are sometimes badly displayed in tree view,
    # see bug report https://github.com/odoo/odoo/issues/8632
    # But is it still true in v9 ?
    amount_currency = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    amount_company_currency = fields.Monetary(
        string="Amount in Company Currency",
        currency_field="company_currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        required=True,
        readonly=True,
        related="payment_line_ids.currency_id",
    )
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Bank Account",
        readonly=True,
        related="payment_line_ids.partner_bank_id",
        check_company=True,
    )
    date = fields.Date(related="payment_line_ids.date", readonly=True)
    communication_type = fields.Selection(
        related="payment_line_ids.communication_type", readonly=True
    )
    communication = fields.Char(string="Communication", required=True, readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="order_id.payment_mode_id.company_id",
        store=True,
        readonly=True,
    )
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="order_id.payment_mode_id.company_id.currency_id",
        readonly=True,
        store=True,
    )

    @api.model
    def same_fields_payment_line_and_bank_payment_line(self):
        """
        This list of fields is used both to compute the grouping
        hashcode and to copy the values from payment line
        to bank payment line
        The fields must have the same name on the 2 objects
        """
        same_fields = [
            "currency_id",
            "partner_id",
            "partner_bank_id",
            "date",
            "communication_type",
        ]
        return same_fields

    @api.depends("payment_line_ids", "payment_line_ids.amount_currency")
    def _compute_amount(self):
        for bline in self:
            amount_currency = sum(bline.mapped("payment_line_ids.amount_currency"))
            amount_company_currency = bline.currency_id._convert(
                amount_currency,
                bline.company_currency_id,
                bline.company_id,
                bline.date or fields.Date.today(),
            )
            bline.amount_currency = amount_currency
            bline.amount_company_currency = amount_company_currency

    @api.model
    @api.returns("self")
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("bank.payment.line") or "New"
            )
        return super(BankPaymentLine, self).create(vals)

    def move_line_offsetting_account_hashcode(self):
        """
        This method is inherited in the module
        account_banking_sepa_direct_debit
        """
        self.ensure_one()
        if self.order_id.payment_mode_id.move_option == "date":
            hashcode = fields.Date.to_string(self.date)
        else:
            hashcode = str(self.id)
        return hashcode

    def reconcile_payment_lines(self):
        for bline in self:
            if all([pline.move_line_id for pline in bline.payment_line_ids]):
                bline.reconcile()
            else:
                bline.no_reconcile_hook()

    def no_reconcile_hook(self):
        """This method is designed to be inherited if needed"""
        return

    def reconcile(self):
        self.ensure_one()
        amlo = self.env["account.move.line"]
        transit_mlines = amlo.search([("bank_payment_line_id", "=", self.id)])
        assert len(transit_mlines) == 1, "We should have only 1 move"
        transit_mline = transit_mlines[0]
        assert not transit_mline.reconciled, "Transit move should not be reconciled"
        lines_to_rec = transit_mline
        for payment_line in self.payment_line_ids:

            if not payment_line.move_line_id:
                raise UserError(
                    _(
                        "Can not reconcile: no move line for "
                        "payment line %s of partner '%s'."
                    )
                    % (payment_line.name, payment_line.partner_id.name)
                )
            if payment_line.move_line_id.reconciled:
                raise UserError(
                    _("Move line '%s' of partner '%s' has already " "been reconciled")
                    % (payment_line.move_line_id.name, payment_line.partner_id.name)
                )
            if payment_line.move_line_id.account_id != transit_mline.account_id:
                raise UserError(
                    _(
                        "For partner '%s', the account of the account "
                        "move line to pay (%s) is different from the "
                        "account of of the transit move line (%s)."
                    )
                    % (
                        payment_line.move_line_id.partner_id.name,
                        payment_line.move_line_id.account_id.code,
                        transit_mline.account_id.code,
                    )
                )

            lines_to_rec += payment_line.move_line_id

        lines_to_rec.reconcile()

    def unlink(self):
        for line in self:
            order_state = line.order_id.state
            if order_state == "uploaded":
                raise UserError(
                    _(
                        "Cannot delete a payment order line whose payment order is"
                        " in state '%s'. You need to cancel it first."
                    )
                    % order_state
                )
        return super(BankPaymentLine, self).unlink()
