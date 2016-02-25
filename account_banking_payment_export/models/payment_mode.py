# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014-2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    type = fields.Many2one(
        'payment.mode.type', string='Export type', required=True,
        help='Select the Export Payment Type for the Payment Mode.')
    payment_order_type = fields.Selection(
        related='type.payment_order_type', readonly=True, string="Order Type",
        help="This field, that comes from export type, determines if this "
             "mode can be selected for customers or suppliers.")
    active = fields.Boolean(string='Active', default=True)
    sale_ok = fields.Boolean(string='Selectable on sale operations',
                             default=True)
    purchase_ok = fields.Boolean(string='Selectable on purchase operations',
                                 default=True)
    note = fields.Text(string="Note", translate=True)
    # Default options for the "payment.order.create" wizard
    default_journal_ids = fields.Many2many(
        'account.journal', string="Journals Filter")
    default_invoice = fields.Boolean(
        string='Linked to an Invoice or Refund', default=False)
    default_date_type = fields.Selection([
        ('due', 'Due'),
        ('move', 'Move'),
        ], default='due', string="Type of Date Filter")
    default_populate_results = fields.Boolean(
        string='Populate Results Directly')
    group_lines = fields.Boolean(
        string="Group lines in payment orders", default=True,
        help="If this mark is checked, the payment order lines will be "
             "grouped when validating the payment order before exporting the "
             "bank file. The grouping will be done only if the following "
             "fields matches:\n"
             "* Partner\n"
             "* Currency\n"
             "* Destination Bank Account\n"
             "* Communication Type (structured, free)\n"
             "* Payment Date\n"
             "(other modules can set additional fields to restrict the "
             "grouping.)")

    @api.onchange('type')
    def type_on_change(self):
        if self.type:
            ajo = self.env['account.journal']
            aj_ids = []
            if self.type.payment_order_type == 'payment':
                aj_ids = ajo.search([
                    ('type', 'in', ('purchase_refund', 'purchase'))]).ids
            elif self.type.payment_order_type == 'debit':
                aj_ids = ajo.search([
                    ('type', 'in', ('sale_refund', 'sale'))]).ids
            self.default_journal_ids = [(6, 0, aj_ids)]
