# Copyright 2017-2020 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    # Local_instrument 'INST' used for instant credit transfers
    # which will begin on November 21st 2017, cf
    # https://www.europeanpaymentscouncil.eu/document-library/
    # rulebooks/2017-sepa-instant-credit-transfer-rulebook
    local_instrument = fields.Selection(
        selection_add=[("INST", "Instant Transfer")],
        ondelete={"INST": "set null"},
    )
