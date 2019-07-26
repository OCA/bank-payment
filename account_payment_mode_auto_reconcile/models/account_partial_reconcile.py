# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


class AccountPartialReconcile(models.Model):

    _inherit = 'account.partial.reconcile'

    payment_mode_auto_reconcile = fields.Boolean()

    @api.model
    def create(self, vals):
        if self.env.context.get('_payment_mode_auto_reconcile'):
            vals['payment_mode_auto_reconcile'] = True
        return super(AccountPartialReconcile, self).create(vals)
