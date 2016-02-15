# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PaymentModeType(models.Model):
    _name = 'payment.mode.type'
    _description = 'Payment Mode Type'

    name = fields.Char('Name', size=64, required=True, help='Payment Type')
    code = fields.Char('Code', size=64, required=True,
                       help='Specify the Code for Payment Type')
    suitable_bank_types = fields.Many2many(
        comodel_name='res.partner.bank.type',
        relation='bank_type_payment_type_rel', column1='pay_type_id',
        column2='bank_type_id', string='Suitable bank types', required=True)
    ir_model_id = fields.Many2one(
        'ir.model', string='Payment wizard',
        help='Select the Payment Wizard for payments of this type. Leave '
             'empty for manual processing',
        domain=[('osv_memory', '=', True)])
    payment_order_type = fields.Selection(
        [('payment', 'Payment'),
         ('debit', 'Debit')],
        string='Order type', required=True, default='payment',
        help="This field determines if this type applies to customers "
             "(Debit) or suppliers (Payment)")
    active = fields.Boolean(string='Active', default=True)

    def _auto_init(self, cr, context=None):
        res = super(PaymentModeType, self)._auto_init(cr, context=context)
        # migrate xmlid from manual_bank_transfer to avoid dependency on
        # account_banking
        cr.execute(
            """UPDATE ir_model_data
            SET module='account_banking_payment_export'
            WHERE module='account_banking' AND
            name='manual_bank_tranfer' AND
            model='payment.mode.type'""")
        return res
