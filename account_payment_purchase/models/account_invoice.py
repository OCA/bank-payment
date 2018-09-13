# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (<http://www.akretion.com>).
# Copyright 2017 Tecnativa - Vicent Cubells.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        new_mode = self.purchase_id.payment_mode_id.id or False
        new_bank = self.purchase_id.supplier_partner_bank_id.id or False
        res = super(AccountInvoice, self).purchase_order_change()
        if self.payment_mode_id and self.payment_mode_id.id != new_mode:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('Selected purchase order have different '
                             'payment mode.'),
            }
            return res
        if self.partner_bank_id and self.partner_bank_id.id != new_bank:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('Selected purchase order have different '
                             'supplier bank.'),
            }
            return res
        self.payment_mode_id = new_mode
        self.partner_bank_id = new_bank
