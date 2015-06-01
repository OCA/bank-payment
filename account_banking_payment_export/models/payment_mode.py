# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#              (C) 2011 - 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, SUPERUSER_ID


class PaymentMode(models.Model):
    """Restoring the payment type from version 5,
    used to select the export wizard (if any)
    """
    _inherit = "payment.mode"

    def _get_manual_bank_transfer(self, cr, uid, context=None):
        """ hack: pre-create the manual bank transfer that is also
        defined in the data directory, so we have an id in to use
        in _auto_init """
        model_data = self.pool['ir.model.data']
        try:
            _, res = model_data.get_object_reference(
                cr, uid,
                'account_banking_payment_export',
                'manual_bank_tranfer')
        except ValueError:
            payment_mode_type = self.pool['payment.mode.type']
            res = payment_mode_type.create(
                cr, uid,
                {'name': 'Manual Bank Transfer',
                 'code': 'BANKMAN'})
            model_data.create(
                cr, uid,
                {'module': 'account_banking_payment_export',
                 'model': 'payment.mode.type',
                 'name': 'manual_bank_tranfer',
                 'res_id': res,
                 'noupdate': False})
        return res

    def _auto_init(self, cr, context=None):
        """ hack: pre-create and initialize the type column so that the
        constraint setting will not fail, this is a hack, made necessary
        because Odoo tries to set the not-null constraint before
        applying default values """
        self._field_create(cr, context=context)
        column_data = self._select_column_data(cr)
        if 'type' not in column_data:
            default_type = self._get_manual_bank_transfer(
                cr, SUPERUSER_ID, context=context)
            if default_type:
                cr.execute('ALTER TABLE "{table}" ADD COLUMN "type" INTEGER'.
                           format(table=self._table))
                cr.execute('UPDATE "{table}" SET type=%s'.
                           format(table=self._table),
                           (default_type,))
        return super(PaymentMode, self)._auto_init(cr, context=context)

    def suitable_bank_types(self, cr, uid, payment_mode_id=None, context=None):
        """ Reinstates functional code for suitable bank type filtering.
        Current code in account_payment is disfunctional.
        """
        res = []
        payment_mode = self.browse(cr, uid, payment_mode_id, context=context)
        if (payment_mode and payment_mode.type and
                payment_mode.type.suitable_bank_types):
            res = [t.code for t in payment_mode.type.suitable_bank_types]
        return res

    @api.model
    def _default_type(self):
        return self.env.ref(
            'account_banking_payment_export.'
            'manual_bank_tranfer', raise_if_not_found=False)\
            or self.env['payment.mode.type']

    type = fields.Many2one(
        'payment.mode.type', string='Export type', required=True,
        help='Select the Export Payment Type for the Payment Mode.',
        default=_default_type)
    payment_order_type = fields.Selection(
        related='type.payment_order_type', readonly=True, string="Order Type",
        selection=[('payment', 'Payment'), ('debit', 'Debit')],
        help="This field, that comes from export type, determines if this "
             "mode can be selected for customers or suppliers.")
    active = fields.Boolean(string='Active', default=True)
    sale_ok = fields.Boolean(string='Selectable on sale operations',
                             default=True)
    purchase_ok = fields.Boolean(string='Selectable on purchase operations',
                                 default=True)
