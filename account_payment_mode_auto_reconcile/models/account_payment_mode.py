# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class AccountPaymentMode(models.Model):

    _inherit = "account.payment.mode"

    auto_reconcile_outstanding_credits = fields.Boolean(
        help="Reconcile automatically outstanding credits when an invoice "
             "using this payment mode is validated, or when this payment mode "
             "is defined on an open invoice."
    )
    auto_reconcile_allow_partial = fields.Boolean(
        default=True,
        help="Allows automatic partial reconciliation of outstanding credits",
    )
