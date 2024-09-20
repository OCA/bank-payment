# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentLine(models.Model):
    _name = "account.payment.line"
    _description = "Payment Lines"
    _check_company_auto = True

    name = fields.Char(string="Payment Reference", readonly=True, copy=False)
    order_id = fields.Many2one(
        comodel_name="account.payment.order",
        string="Payment Order",
        ondelete="cascade",
        index=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        related="order_id.company_id", store=True, readonly=True
    )
    company_currency_id = fields.Many2one(
        related="order_id.company_currency_id", store=True, readonly=True
    )
    payment_type = fields.Selection(
        related="order_id.payment_type", store=True, readonly=True
    )
    bank_account_required = fields.Boolean(
        related="order_id.payment_method_id.bank_account_required", readonly=True
    )
    state = fields.Selection(
        related="order_id.state", string="State", readonly=True, store=True
    )
    move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Journal Item",
        ondelete="restrict",
        check_company=True,
    )
    ml_maturity_date = fields.Date(related="move_line_id.date_maturity", readonly=True)
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency of the Payment Transaction",
        required=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
    amount_currency = fields.Monetary(string="Amount", currency_field="currency_id")
    amount_company_currency = fields.Monetary(
        compute="_compute_amount_company_currency",
        string="Amount in Company Currency",
        currency_field="company_currency_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        domain=[("parent_id", "=", False)],
        check_company=True,
    )
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Partner Bank Account",
        required=False,
        ondelete="restrict",
        check_company=True,
    )
    date = fields.Date(string="Payment Date")
    # communication field is required=False because we don't want to block
    # the creation of lines from move/invoices when communication is empty
    # This field is required in the form view and there is an error message
    # when going from draft to confirm if the field is empty
    communication = fields.Char(
        required=False, help="Label of the payment that will be seen by the destinee"
    )
    communication_type = fields.Selection(
        selection=[("normal", "Free")], required=True, default="normal"
    )
    payment_ids = fields.Many2many(
        comodel_name="account.payment",
        string="Payment transaction",
        readonly=True,
    )

    _sql_constraints = [
        (
            "name_company_unique",
            "unique(name, company_id)",
            "A payment line already exists with this reference in the same company!",
        )
    ]

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("account.payment.line") or "New"
            )
        return super(AccountPaymentLine, self).create(vals)

    @api.depends("amount_currency", "currency_id", "company_currency_id", "date")
    def _compute_amount_company_currency(self):
        for line in self:
            if line.currency_id and line.company_currency_id:
                line.amount_company_currency = line.currency_id._convert(
                    line.amount_currency,
                    line.company_currency_id,
                    line.company_id,
                    line.date or fields.Date.today(),
                )
            else:
                line.amount_company_currency = 0

    @api.model
    def _get_payment_line_grouping_fields(self):
        """This list of fields is used o compute the grouping hashcode."""
        return [
            "currency_id",
            "partner_id",
            "partner_bank_id",
            "date",
            "communication_type",
        ]

    def payment_line_hashcode(self):
        self.ensure_one()
        values = []
        for field in self._get_payment_line_grouping_fields():
            values.append(str(self[field]))
        # Don't group the payment lines that are attached to the same supplier
        # but to move lines with different accounts (very unlikely),
        # for easier generation/comprehension of the transfer move
        values.append(str(self.move_line_id.account_id or False))
        # Don't group the payment lines that use a structured communication
        # otherwise it would break the structured communication system !
        if self.communication_type != "normal":
            values.append(str(self.id))
        return "-".join(values)

    @api.onchange("partner_id")
    def partner_id_change(self):
        partner_bank = False
        if self.partner_id.bank_ids:
            partner_bank = self.partner_id.bank_ids.filtered(
                lambda bank: not bank.company_id or bank.company_id == self.company_id
            )[:1]
        self.partner_bank_id = partner_bank

    @api.onchange("move_line_id")
    def move_line_id_change(self):
        if self.move_line_id:
            vals = self.move_line_id._prepare_payment_line_vals(self.order_id)
            vals.pop("order_id")
            for field, value in vals.items():
                self[field] = value
        else:
            self.partner_id = False
            self.partner_bank_id = False
            self.amount_currency = 0.0
            self.currency_id = self.env.user.company_id.currency_id
            self.communication = False

    def invoice_reference_type2communication_type(self):
        """This method is designed to be inherited by
        localization modules"""
        # key = value of 'reference_type' field on account_invoice
        # value = value of 'communication_type' field on account_payment_line
        res = {"none": "normal", "structured": "structured"}
        return res

    def draft2open_payment_line_check(self):
        self.ensure_one()
        if self.bank_account_required and not self.partner_bank_id:
            raise UserError(
                _("Missing Partner Bank Account on payment line %s") % self.name
            )
        if not self.communication:
            raise UserError(_("Communication is empty on payment line %s.") % self.name)

    def _prepare_account_payment_vals(self):
        """Prepare the dictionary to create an account payment record from a set of
        payment lines.
        """
        journal = self.order_id.journal_id
        payment_mode = self.order_id.payment_mode_id
        vals = {
            "payment_type": self.order_id.payment_type,
            "partner_id": self.partner_id.id,
            "destination_account_id": self.move_line_id.account_id.id,
            "company_id": self.order_id.company_id.id,
            "amount": sum(self.mapped("amount_currency")),
            "date": fields.Date.today(),
            "currency_id": self.currency_id.id,
            "ref": self.order_id.name,
            "payment_reference": " - ".join([line.communication for line in self]),
            "journal_id": journal.id,
            "partner_bank_id": self.partner_bank_id.id,
            "payment_order_id": self.order_id.id,
            "payment_line_ids": [(6, 0, self.ids)],
        }
        # Determine payment method line according payment method and journal
        line = self.env["account.payment.method.line"].search(
            [
                ("payment_method_id", "=", payment_mode.payment_method_id.id),
                ("journal_id", "=", journal.id),
            ],
            limit=1,
        )
        if line:
            vals["payment_method_line_id"] = line.id
        # Determine partner_type
        move_type = self[:1].move_line_id.move_id.move_type
        if move_type in {"out_invoice", "out_refund"}:
            vals["partner_type"] = "customer"
        elif move_type in {"in_invoice", "in_refund"}:
            vals["partner_type"] = "supplier"
        else:
            p_type = "customer" if vals["payment_type"] == "inbound" else "supplier"
            vals["partner_type"] = p_type
        # Fill destination account if manual payment line with no linked journal item
        if not vals["destination_account_id"]:
            if vals["partner_type"] == "customer":
                vals[
                    "destination_account_id"
                ] = self.partner_id.property_account_receivable_id.id
            else:
                vals[
                    "destination_account_id"
                ] = self.partner_id.property_account_payable_id.id
        return vals
