# Copyright 2024-2025 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Tecnativa - Carlos Dauden, Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"
    _check_company_auto = True

    # START inherit of native fields
    name = fields.Char(translate=True)
    journal_id = fields.Many2one(
        domain="[('id', 'in', filter_journal_ids)]",
    )
    company_id = fields.Many2one(
        "res.company",
        related=False,  # native: related='journal_id.company_id'
        required=True,
        compute="_compute_company_id",  # for smooth post-install
        store=True,
        precompute=True,
        readonly=False,
    )
    # END inherit of native fields
    # Here is the strategy to support bank_account_link = variable
    # without breaking the native behavior
    # In the account module, company_id is a related of journal_id.company_id
    # In this module, company_id becomes a computed field
    # When bank_account_link = 'fixed' => we use journal_id
    # When bank_account_link = 'variable':
    # - variable_journal_ids has the list of allowed journals on payment order
    # - journal_id is optional ; it is a "default journal"
    filter_journal_ids = fields.Many2many(
        "account.journal", compute="_compute_filter_journal_ids"
    )
    bank_account_link = fields.Selection(
        [("fixed", "Fixed"), ("variable", "Variable")],
        string="Link to Bank Account",
        required=True,
        default="fixed",
        help="For payment modes that are always attached to the same bank "
        "account of your company (such as wire transfer from customers or "
        "SEPA direct debit from suppliers), select "
        "'Fixed'. For payment modes that are not always attached to the same "
        "bank account (such as SEPA Direct debit for customers, wire transfer "
        "to suppliers), you should select 'Variable', which means that you "
        "will select the bank account on the payment order. If your company "
        "only has one bank account, you should always select 'Fixed'.",
    )
    # I need to explicitly define the table name
    # because I have 2 M2M fields pointing to account.journal
    variable_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="account_payment_method_line_variable_journal_rel",
        column1="method_line_id",
        column2="journal_id",
        string="Allowed Bank Journals",
        domain="[('id', 'in', filter_journal_ids)]",
        check_company=True,
        compute="_compute_variable_journal_ids",
        store=True,
        readonly=False,
        precompute=True,
    )
    active = fields.Boolean(default=True)
    selectable = fields.Boolean(string="Selectable on Partners/Invoices")
    report_description = fields.Html(translate=True)
    show_bank_account = fields.Selection(
        selection=[
            ("full", "Full"),
            ("first", "First n chars"),
            ("last", "Last n chars"),
            ("first_last", "First n chars and Last n chars"),
            ("no", "No"),
        ],
        default="full",
        string="Show Customer Bank Account",
        help="On invoice report, show partial or full bank account number.",
    )
    show_bank_account_chars = fields.Integer(
        string="# of Digits to Show for Customer Bank Account",
        default=4,
    )
    refund_payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line",
        domain="[('payment_type', '!=', payment_type)]",
        string="Payment Mode for Refunds",
        help="This payment mode will be used when doing "
        "refunds coming from the current payment mode.",
        check_company=True,
    )

    _sql_constraints = [
        (
            "show_bank_account_chars_positive",
            "CHECK(show_bank_account_chars >= 0)",
            "The number of digits to show for customer bank account "
            "must be positive or null.",
        )
    ]

    @api.constrains(
        "bank_account_link",
        "journal_id",
        "variable_journal_ids",
        "payment_method_id",
    )
    def _check_payment_method_line(self):
        for line in self:
            # I cannot check line.journal_id.bank_account_id when
            # line.bank_account_link == "fixed" because method lines are
            # auto-created on bank journal creation and the bank account
            # but not be configured yet.
            if line.bank_account_link == "fixed" and not line.journal_id:
                raise ValidationError(
                    _(
                        "On %(name)s, the journal is not set.",
                        name=line.display_name,
                    )
                )
            if (
                line.bank_account_link == "variable"
                and line.journal_id
                and line.journal_id not in line.variable_journal_ids
            ):
                raise ValidationError(
                    _(
                        "On %(name)s, the default journal '%(default_journal)s' is "
                        "not part of the allowed bank journals.",
                        name=line.display_name,
                        default_journal=line.journal_id.display_name,
                    )
                )
            if line.payment_method_id.bank_account_required:
                if line.bank_account_link == "variable":
                    for journal in line.variable_journal_ids:
                        if not journal.bank_account_id:
                            raise ValidationError(
                                _(
                                    "On %(name)s, the Payment Method %(method)s is "
                                    "configured with Bank Account Required but journal "
                                    "%(journal)s is not linked to a bank account.",
                                    name=line.display_name,
                                    method=line.payment_method_id.display_name,
                                    journal=journal.display_name,
                                )
                            )

    @api.depends("bank_account_link")
    def _compute_variable_journal_ids(self):
        for line in self:
            if line.bank_account_link == "fixed":
                line.variable_journal_ids = [Command.clear()]

    @api.depends("journal_id")
    def _compute_company_id(self):
        for line in self:
            if line.journal_id:
                line.company_id = line.journal_id.company_id.id
            else:
                line.company_id = self.env.company.id

    @api.depends("payment_method_id", "company_id")
    def _compute_filter_journal_ids(self):
        infos = self.env["account.payment.method"]._get_payment_method_information()
        for line in self:
            domain = []
            if line.company_id:
                domain.append(("company_id", "=", line.company_id.id))
            if line.payment_method_id:
                journal_types = infos.get(line.payment_method_id.code, {}).get("type")
                if journal_types:
                    domain.append(("type", "in", journal_types))
                else:
                    domain.append(("type", "in", ("bank", "cash", "credit")))
                if line.payment_method_id.bank_account_required:
                    domain.append(("bank_account_id", "!=", False))
            else:
                domain.append(("type", "in", ("bank", "cash", "credit")))
            line.filter_journal_ids = self.env["account.journal"].search(domain).ids

    def _compute_display_name(self):
        if self.env.context.get("hide_payment_journal_id"):
            return super()._compute_display_name()
        for line in self:
            if line.bank_account_link == "fixed" and line.journal_id:
                line.display_name = f"{line.name} ({line.journal_id.name})"
            else:
                line.display_name = f"{line.name}"
