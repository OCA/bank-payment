# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Partner Bank Account",
        compute="_compute_partner_bank_id",
        readonly=False,
        store=True,
        help="Bank account on which we should pay the supplier",
        check_company=True,
    )
    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="move_line_id",
        string="Payment lines",
        check_company=True,
    )

    @api.depends("move_id", "move_id.partner_bank_id", "move_id.payment_mode_id")
    def _compute_partner_bank_id(self):
        for ml in self:
            if (
                ml.move_id.move_type in ("in_invoice", "in_refund")
                and not ml.reconciled
                and (ml.payment_mode_id.payment_order_ok or not ml.payment_mode_id)
                and ml.account_id.internal_type in ("receivable", "payable")
                and not any(
                    p_state in ("draft", "open", "generated")
                    for p_state in ml.payment_line_ids.mapped("state")
                )
            ):
                ml.partner_bank_id = ml.move_id.partner_bank_id.id
            else:
                ml.partner_bank_id = ml.partner_bank_id

    def _get_communication(self):
        """
        Retrieve the communication string for the payment order
        """
        aplo = self.env["account.payment.line"]
        # default values for communication_type and communication
        communication_type = "normal"
        communication = self.move_id._get_payment_order_communication_full()
        # change these default values if move line is linked to an invoice
        if self.move_id.is_invoice():
            if (self.move_id.reference_type or "none") != "none":
                ref2comm_type = aplo.invoice_reference_type2communication_type()
                communication_type = ref2comm_type[self.move_id.reference_type]
        return communication_type, communication

    def _prepare_payment_line_vals(self, payment_order):
        self.ensure_one()
        communication_type, communication = self._get_communication()
        if self.currency_id:
            currency_id = self.currency_id.id
            amount_currency = self.amount_residual_currency
        else:
            currency_id = self.company_id.currency_id.id
            amount_currency = self.amount_residual
            # TODO : check that self.amount_residual_currency is 0
            # in this case
        if payment_order.payment_type == "outbound":
            amount_currency *= -1
        partner_bank_id = self.partner_bank_id.id
        if not partner_bank_id:
            partner_bank_id = self.partner_id.bank_ids.filtered(
                lambda bank: not bank.company_id or bank.company_id == self.company_id
            )[:1].id
        vals = {
            "order_id": payment_order.id,
            "partner_bank_id": partner_bank_id,
            "partner_id": self.partner_id.id,
            "move_line_id": self.id,
            "communication": communication,
            "communication_type": communication_type,
            "currency_id": currency_id,
            "amount_currency": amount_currency,
            "date": False,
            # date is set when the user confirms the payment order
        }
        return vals

    def create_payment_line_from_move_line(self, payment_order):
        vals_list = []
        for mline in self:
            vals_list.append(mline._prepare_payment_line_vals(payment_order))
        return self.env["account.payment.line"].create(vals_list)
