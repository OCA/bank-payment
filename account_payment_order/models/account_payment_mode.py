# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2014-2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    """This corresponds to the object payment.mode of v8 with some
    important changes"""

    _inherit = "account.payment.mode"

    payment_order_ok = fields.Boolean(
        string="Selectable in Payment Orders", default=True
    )
    no_debit_before_maturity = fields.Boolean(
        string="Disallow Debit Before Maturity Date",
        help="If you activate this option on an Inbound payment mode, "
        "you will have an error message when you confirm a debit order "
        "that has a payment line with a payment date before the maturity "
        "date.",
    )
    # Default options for the "payment.order.create" wizard
    default_payment_mode = fields.Selection(
        selection=[("same", "Same"), ("same_or_null", "Same or empty"), ("any", "Any")],
        string="Payment Mode on Invoice",
        default="same",
    )
    default_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        string="Journals Filter",
        domain="[('company_id', '=', company_id)]",
    )
    default_invoice = fields.Boolean(
        string="Linked to an Invoice or Refund", default=False
    )
    default_target_move = fields.Selection(
        selection=[("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        default="posted",
    )
    default_date_type = fields.Selection(
        selection=[("due", "Due"), ("move", "Move")],
        default="due",
        string="Type of Date Filter",
    )
    # default option for account.payment.order
    default_date_prefered = fields.Selection(
        selection=[
            ("now", "Immediately"),
            ("due", "Due Date"),
            ("fixed", "Fixed Date"),
        ],
        string="Default Payment Execution Date",
    )
    group_lines = fields.Boolean(
        string="Group Transactions in Payment Orders",
        default=True,
        help="If this mark is checked, the transaction lines of the "
        "payment order will be grouped upon confirmation of the payment "
        "order.The grouping will be done only if the following "
        "fields matches:\n"
        "* Partner\n"
        "* Currency\n"
        "* Destination Bank Account\n"
        "* Payment Date\n"
        "and if the 'Communication Type' is 'Free'\n"
        "(other modules can set additional fields to restrict the "
        "grouping.)",
    )
    generate_move = fields.Boolean(
        string="Generate Accounting Entries On File Upload", default=True
    )
    offsetting_account = fields.Selection(
        selection=[
            ("bank_account", "Bank Account"),
            ("transfer_account", "Transfer Account"),
        ],
        default="bank_account",
    )
    transfer_account_id = fields.Many2one(
        comodel_name="account.account",
        domain=[("reconcile", "=", True)],
        help="Pay off lines in 'file uploaded' payment orders with a move on "
        "this account. You can only select accounts "
        "that are marked for reconciliation",
    )
    transfer_journal_id = fields.Many2one(
        comodel_name="account.journal",
        help="Journal to write payment entries when confirming "
        "payment/debit orders of this mode",
    )
    move_option = fields.Selection(
        selection=[
            ("date", "One move per payment date"),
            ("line", "One move per payment line"),
        ],
        default="date",
    )
    post_move = fields.Boolean(default=True)

    @api.constrains(
        "generate_move",
        "offsetting_account",
        "transfer_account_id",
        "transfer_journal_id",
        "move_option",
    )
    def transfer_move_constrains(self):
        for mode in self:
            if mode.generate_move:
                if not mode.offsetting_account:
                    raise ValidationError(
                        _(
                            "On the payment mode '%s', you must select an "
                            "option for the 'Offsetting Account' parameter"
                        )
                        % mode.name
                    )
                elif mode.offsetting_account == "transfer_account":
                    if not mode.transfer_account_id:
                        raise ValidationError(
                            _(
                                "On the payment mode '%s', you must "
                                "select a value for the 'Transfer Account'."
                            )
                            % mode.name
                        )
                    if not mode.transfer_journal_id:
                        raise ValidationError(
                            _(
                                "On the payment mode '%s', you must "
                                "select a value for the 'Transfer Journal'."
                            )
                            % mode.name
                        )
                if not mode.move_option:
                    raise ValidationError(
                        _(
                            "On the payment mode '%s', you must "
                            "choose an option for the 'Move Option' "
                            "parameter."
                        )
                        % mode.name
                    )

    @api.onchange("payment_method_id")
    def payment_method_id_change(self):
        if self.payment_method_id:
            ajo = self.env["account.journal"]
            aj_ids = []
            if self.payment_method_id.payment_type == "outbound":
                aj_ids = ajo.search(
                    [
                        ("type", "in", ("purchase_refund", "purchase")),
                        ("company_id", "=", self.company_id.id),
                    ]
                ).ids
            elif self.payment_method_id.payment_type == "inbound":
                aj_ids = ajo.search(
                    [
                        ("type", "in", ("sale_refund", "sale")),
                        ("company_id", "=", self.company_id.id),
                    ]
                ).ids
            self.default_journal_ids = [(6, 0, aj_ids)]

    @api.onchange("generate_move")
    def generate_move_change(self):
        if self.generate_move:
            # default values
            self.offsetting_account = "bank_account"
            self.move_option = "date"
        else:
            self.offsetting_account = False
            self.transfer_account_id = False
            self.transfer_journal_id = False
            self.move_option = False

    @api.onchange("offsetting_account")
    def offsetting_account_change(self):
        if self.offsetting_account == "bank_account":
            self.transfer_account_id = False
            self.transfer_journal_id = False
