# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (www.akretion.com)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    check_number = fields.Integer(
        string="Check Number", copy=False, default=0,
        readonly=True, states={'draft': [('readonly', False)]},
        help="Number of the first check corresponding to this payment.")
    payment_method_code = fields.Char(
        related='payment_method_id.code',
        readonly=True,
    )

    @api.multi
    def generate_payment_file(self):
        """Creates the Check file!"""
        self.ensure_one()
        if self.payment_method_id.code != 'check_printing':
            return super().generate_payment_file()
        lines = self.bank_line_ids
        check_number = self.check_number or 0
        for line in lines:
            line.write({'check_number': check_number})
            check_number += 1
        file_value = self.env['ir.actions.report']._get_report_from_name(
            self.payment_mode_id.check_layout_id.report
        ).with_context(active_model=lines._name).render(lines.ids)[0]
        filename = 'check_print.pdf'
        return (file_value, filename)
