# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="move_line_id",
        string="Payment lines",
        check_company=True,
    )

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
        vals = {
            "order_id": payment_order.id,
            "move_line_id": self.id,
        }
        return vals

    def create_payment_line_from_move_line(self, payment_order):
        vals_list = []
        for mline in self:
            vals_list.append(mline._prepare_payment_line_vals(payment_order))
        return self.env["account.payment.line"].create(vals_list)
