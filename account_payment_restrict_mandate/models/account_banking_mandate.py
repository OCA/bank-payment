# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from dateutil import rrule
from openerp import _, api, fields, models, tools
from openerp.exceptions import ValidationError
from openerp.addons import decimal_precision
_logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    _inherit = 'account.banking.mandate'

    @api.depends('repetition_rule')
    @api.multi
    def _compute_rrule(self):
        for this in self:
            parameters = dict(this.repetition_rule or {})
            if not parameters:
                continue
            parameters.setdefault(
                'dtstart', fields.Date.from_string(this.date_start))
            this.rrule = rrule.rrule(**parameters)

    @api.depends(
        'repetition_rule', 'max_amount_per_date', 'date_start',
        'date_end')
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
    # this is a hack until we have a widget to edit rrules
    repetition_rule_text = fields.Text(
        string='Repetition',
        compute=lambda self: [
            this.update({'repetition_rule_text': str(this.repetition_rule)})
            for this in self
        ],
        inverse=lambda self: [
            this.write({
                'repetition_rule': tools.safe_eval.safe_eval(
                    this.repetition_rule_text),
            })
            for this in self
        ],
        default=lambda self: self._fields['repetition_rule'].default(self))
    repetition_rule = fields.Serialized(
        'Repetition', default={
            'freq': rrule.MONTHLY,
            'interval': 1,
            'bymonthday': 1,
        })
    rrule = fields.Serialized(compute=_compute_rrule)

    @api.constrains('repetition_rule')
    def _constrain_repetition_rule(self):
        if not isinstance(self.repetition_rule, dict):
            raise ValidationError(_('Invalid rrule!'))
        try:
            self._compute_rrule()
        except:
            _logger.exception('Invalid rrule')
            raise ValidationError(_('Invalid rrule!'))
