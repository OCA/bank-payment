# -*- coding: utf-8 -*-
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.multi
    def action_move_create(self):
        result = super(HrExpense, self).action_move_create()

        for record in self:
            for line in record.account_move_id.line_ids:
                line.partner_bank_id = record.employee_id.bank_account_id

        return result
