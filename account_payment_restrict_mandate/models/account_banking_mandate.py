# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import _, api, fields, models, tools
from openerp.exceptions import ValidationError
from openerp.addons import decimal_precision
from openerp.addons.field_rrule import FieldRRule
_logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    _inherit = 'account.banking.mandate'

    @api.depends(
        'rrule', 'max_amount_per_date', 'date_start', 'date_end')
    @api.multi
    def _compute_max_amount(self):
        for this in self:
            if not this.date_start or not this.date_end or not this.rrule:
                continue
            occurrences = len(list(
                this.rrule.between(
                    fields.Datetime.from_string(this.date_start),
                    fields.Datetime.from_string(this.date_end),
                    inc=True,
                )))
            this.max_amount = this.max_amount_per_date * occurrences

    date_start = fields.Datetime('Start')
    date_end = fields.Datetime('End')
    max_amount = fields.Float(
        'Maximum amount', compute=_compute_max_amount,
        digits=decimal_precision.get_precision('Account'))
    max_amount_per_date = fields.Float(
        'Maximum amount per date',
        digits=decimal_precision.get_precision('Account'),
        help='This is the maximum amount allowed to withdraw per occassion')
    rrule = FieldRRule('Installments')
