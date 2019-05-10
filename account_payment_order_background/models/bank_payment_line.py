# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    @api.multi
    def reconcile(self):
        # Propagate __reconcile_as_job when the reconcile is done
        # from a payment order so the lines will be reconciled in jobs
        # (one per one).
        # The reconciliation is slow and might update sale.order.line's
        # invoiced field, locking the sale.order.line table for all the
        # duration of the AccountPaymentOrder.generated2uploaded method
        # so this shorten the duration of the locks.
        return super(
            BankPaymentLine, self.with_context(__reconcile_as_job=True)
        ).reconcile()
