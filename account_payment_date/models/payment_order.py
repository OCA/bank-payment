# -*- coding: utf-8 -*-
# © <2018> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    allow_force_date = fields.Boolean('Allow force accounting date')


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    def get_account_date(self):
        if self.payment_mode_id.allow_force_date:
            return self.date_scheduled

    @api.multi
    @api.constrains('date_scheduled')
    def check_date_scheduled(self):
        today = fields.Date.context_today(self)
        for order in self:
            if order.payment_mode_id.allow_force_date:
                return True
            if order.date_scheduled:
                if order.date_scheduled < today:
                    raise ValidationError(_(
                        "On payment order %s, the Payment Execution Date "
                        "is in the past (%s).")
                        % (order.name, order.date_scheduled))

    @api.multi
    def _prepare_move_line_offsetting_account(
            self, amount_company_currency, amount_payment_currency,
            bank_lines):
        vals = super(AccountPaymentOrder,
                     self)._prepare_move_line_offsetting_account(
                         amount_company_currency,
                         amount_payment_currency, bank_lines)
        if self.payment_mode_id.allow_force_date:
            vals.update({'date': self.date_scheduled or bank_lines[0].date})
        return vals

    @api.multi
    def _prepare_move_line_partner_account(self, bank_line):
        vals = super(AccountPaymentOrder,
                     self)._prepare_move_line_partner_account(bank_line)
        if self.payment_mode_id.allow_force_date:
            vals.update({'date': self.get_account_date()})
        return vals

    @api.multi
    def _prepare_move(self, bank_lines=None):
        move = super(AccountPaymentOrder, self)._prepare_move(bank_lines)
        if self.payment_mode_id.allow_force_date:
            move.update({'date': self.get_account_date()})
        return move
