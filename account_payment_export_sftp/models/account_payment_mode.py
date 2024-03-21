from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    edi_exchange_type_id = fields.Many2one(
        "edi.exchange.type",
        help="Define which rule it should use to send the file.",
        domain=[("backend_id", "!=", False), ("direction", "=", "output")],
    )

    disable_edi_auto = fields.Boolean(
        help="When marked, EDI could be avoided",
        default=True,
    )
