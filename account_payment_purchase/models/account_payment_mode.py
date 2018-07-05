# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PaymentMode(models.Model):

    _inherit = "account.payment.mode"

    purchase_ok = fields.Boolean(string='Selectable on purchase operations',
                                 default=False)
