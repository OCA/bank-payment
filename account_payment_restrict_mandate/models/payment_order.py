# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    restrict_mandate_messages = fields.Html('Mandate restrictions')
