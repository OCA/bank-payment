# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInternalTransfer(models.Model):
    _name = "account.internal.transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Internal Transfer"
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(
        string="Name",
        related="move_id.name",
        copy=False,
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        readonly=True,
        default=lambda self: self.env.company,
    )
    transfer_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Transfer Journal",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    outgoing_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Outgoing Journal",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    destination_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Destination Journal",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    outgoing_partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Outgoing Bank Account",
        check_company=True,
        related="outgoing_journal_id.bank_account_id",
        store=True,
        readonly=True,
    )
    destination_partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Destination Bank Account",
        check_company=True,
        related="destination_journal_id.bank_account_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
        related="company_id.currency_id",
        store=True,
    )
    amount = fields.Monetary(
        currency_field="currency_id",
        string="Amount",
        required=True,
        default=0.0,
    )
    date = fields.Date(
        string="Date",
        required=True,
    )
    date_maturity = fields.Date(
        string="Due Date",
        required=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Journal Entry",
        readonly=True,
        ondelete="cascade",
        check_company=True,
    )
    state = fields.Selection(
        string="Status",
        default="draft",
        related="move_id.state",
        copy=False,
        readonly=True,
        store=True,
        tracking=True,
    )

    def _create_account_move(self):
        move_vals = {
            "date": self.date,
            "journal_id": self.transfer_journal_id.id,
            "ref": "Internal Transfer",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Transfer to " + self.destination_journal_id.name,
                        "account_id": self.company_id.transfer_payable_account_id.id,
                        "partner_id": self.company_id.partner_id.id,
                        "debit": 0.0,
                        "credit": self.amount,
                        "date_maturity": self.date_maturity,
                        "partner_bank_id": self.destination_partner_bank_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Transfer from " + self.outgoing_journal_id.name,
                        "account_id": self.company_id.transfer_receivable_account_id.id,
                        "partner_id": self.company_id.partner_id.id,
                        "debit": self.amount,
                        "credit": 0.0,
                        "date_maturity": self.date_maturity,
                        "partner_bank_id": self.outgoing_partner_bank_id.id,
                    },
                ),
            ],
        }
        move_id = self.env["account.move"].create(move_vals)
        return move_id

    @api.model
    def create(self, vals):
        record = super(AccountInternalTransfer, self).create(vals)
        move_id = record._create_account_move()
        record.move_id = move_id
        return record

    def _syncronize_account_move(self):
        if self.move_id.id:
            move = self.env["account.move"].browse(self.move_id.id)
            credit_line = move.line_ids.filtered(lambda x: x.credit > 0)
            debit_line = move.line_ids.filtered(lambda x: x.debit > 0)
            move.write(
                {
                    "date": self.date,
                    "journal_id": self.transfer_journal_id.id,
                    "line_ids": [
                        (
                            1,
                            credit_line.id,
                            {
                                "name": "Transfer to "
                                + self.destination_journal_id.name,
                                "credit": self.amount,
                                "date_maturity": self.date_maturity,
                                "partner_bank_id": self.destination_partner_bank_id.id,
                            },
                        ),
                        (
                            1,
                            debit_line.id,
                            {
                                "name": "Transfer from "
                                + self.outgoing_journal_id.name,
                                "debit": self.amount,
                                "date_maturity": self.date_maturity,
                                "partner_bank_id": self.outgoing_partner_bank_id.id,
                            },
                        ),
                    ],
                }
            )

    def write(self, vals):
        res = super(AccountInternalTransfer, self).write(vals)
        if "move_id" not in vals:
            self._syncronize_account_move()
        return res

    def action_confirm(self):
        if self.move_id:
            self.move_id.action_post()

    def action_cancel(self):
        if self.move_id:
            self.move_id.button_cancel()

    def action_draft(self):
        if self.move_id:
            self.move_id.button_draft()
