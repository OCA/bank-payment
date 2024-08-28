# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2014-2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    payment_order_ok = fields.Boolean(
        string="Selectable in Payment Orders",
        compute="_compute_payment_order_ok",
        store=True,
        readonly=False,
        precompute=True,
    )
    specific_sequence_id = fields.Many2one(
        "ir.sequence",
        check_company=True,
        copy=False,
        help="If left empty, the payment orders with this payment mode will use the "
        "generic sequence for all payment orders.",
    )
    no_debit_before_maturity = fields.Boolean(
        string="Disallow Debit Before Maturity Date",
        default=True,
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
        compute="_compute_default_journal_ids",
        store=True,
        readonly=False,
        precompute=True,
        string="Journals Filter",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
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

    @api.depends("payment_method_id")
    def _compute_payment_order_ok(self):
        for mode in self:
            mode.payment_order_ok = mode.payment_method_id.payment_order_ok

    @api.depends("payment_method_id", "company_id")
    def _compute_default_journal_ids(self):
        ptype_map = {
            "outbound": "purchase",
            "inbound": "sale",
        }
        for mode in self:
            if (
                mode.payment_method_id
                and mode.payment_method_id.payment_type in ptype_map
            ):
                mode.default_journal_ids = (
                    self.env["account.journal"]
                    .search(
                        [
                            (
                                "type",
                                "=",
                                ptype_map[mode.payment_method_id.payment_type],
                            ),
                            ("company_id", "=", mode.company_id.id),
                        ]
                    )
                    .ids
                )
