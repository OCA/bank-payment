# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, workflow, _
try:
    # This is to avoid the drop of the column total each time you update
    # the module account_payment, because the store attribute is set later
    # and Odoo doesn't defer this removal
    from openerp.addons.account_payment.account_payment import payment_order
    payment_order._columns['total'].nodrop = True
except ImportError:
    pass


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    payment_order_type = fields.Selection(
        [('payment', 'Payment'), ('debit', 'Direct debit')],
        'Payment order type', required=True, default='payment',
        readonly=True, states={'draft': [('readonly', False)]})
    mode_type = fields.Many2one('payment.mode.type', related='mode.type',
                                string='Payment Type')
    bank_line_ids = fields.One2many(
        'bank.payment.line', 'order_id', string="Bank Payment Lines",
        readonly=True)
    total = fields.Float(compute='_compute_total', store=True)
    bank_line_count = fields.Integer(
        compute='_bank_line_count', string='Number of Bank Lines')

    @api.depends('line_ids', 'line_ids.amount')
    @api.one
    def _compute_total(self):
        self.total = sum(self.mapped('line_ids.amount') or [0.0])

    @api.multi
    @api.depends('bank_line_ids')
    def _bank_line_count(self):
        for order in self:
            order.bank_line_count = len(order.bank_line_ids)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise exceptions.Warning(
                    _("You cannot remove any order that is not in 'draft' or "
                      "'cancel' state."))
        return super(PaymentOrder, self).unlink()

    @api.multi
    def launch_wizard(self):
        """Search for a wizard to launch according to the type.
        If type is manual. just confirm the order.
        Previously (pre-v6) in account_payment/wizard/wizard_pay.py
        """
        context = self.env.context.copy()
        order = self[0]
        # check if a wizard is defined for the first order
        if order.mode.type and order.mode.type.ir_model_id:
            context['active_ids'] = self.ids
            wizard_model = order.mode.type.ir_model_id.model
            wizard_obj = self.env[wizard_model]
            return {
                'name': wizard_obj._description or _('Payment Order Export'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': wizard_model,
                'domain': [],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'nodestroy': True,
            }
        else:
            # should all be manual orders without type or wizard model
            for order in self[1:]:
                if order.mode.type and order.mode.type.ir_model_id:
                    raise exceptions.Warning(
                        _('Error'),
                        _('You can only combine payment orders of the same '
                          'type'))
            # process manual payments
            for order_id in self.ids:
                workflow.trg_validate(self.env.uid, 'payment.order',
                                      order_id, 'done', self.env.cr)
            return {}

    @api.multi
    def action_done(self):
        self.write({
            'date_done': fields.Date.context_today(self),
            'state': 'done',
            })
        return True

    @api.multi
    def action_cancel(self):
        for order in self:
            order.write({'state': 'cancel'})
            order.bank_line_ids.unlink()
        return True

    @api.model
    def _prepare_bank_payment_line(self, paylines):
        return {
            'order_id': paylines[0].order_id.id,
            'payment_line_ids': [(6, 0, paylines.ids)],
            'communication': '-'.join(
                [line.communication for line in paylines]),
            }

    @api.multi
    def action_open(self):
        """
        Called when you click on the 'Confirm' button
        Set the 'date' on payment line depending on the 'date_prefered'
        setting of the payment.order
        Re-generate the bank payment lines
        """
        res = super(PaymentOrder, self).action_open()
        bplo = self.env['bank.payment.line']
        today = fields.Date.context_today(self)
        for order in self:
            # Delete existing bank payment lines
            order.bank_line_ids.unlink()
            # Create the bank payment lines from the payment lines
            group_paylines = {}  # key = hashcode
            for payline in order.line_ids:
                # Compute requested payment date
                if order.date_prefered == 'due':
                    requested_date = payline.ml_maturity_date or today
                elif order.date_prefered == 'fixed':
                    requested_date = order.date_scheduled or today
                else:
                    requested_date = today
                # No payment date in the past
                if requested_date < today:
                    requested_date = today
                # Write requested_date on 'date' field of payment line
                payline.date = requested_date
                # Group options
                if order.mode.group_lines:
                    hashcode = payline.payment_line_hashcode()
                else:
                    # Use line ID as hascode, which actually means no grouping
                    hashcode = payline.id
                if hashcode in group_paylines:
                    group_paylines[hashcode]['paylines'] += payline
                    group_paylines[hashcode]['total'] +=\
                        payline.amount_currency
                else:
                    group_paylines[hashcode] = {
                        'paylines': payline,
                        'total': payline.amount_currency,
                    }
            # Create bank payment lines
            for paydict in group_paylines.values():
                # Block if a bank payment line is <= 0
                if paydict['total'] <= 0:
                    raise exceptions.Warning(_(
                        "The amount for Partner '%s' is negative "
                        "or null (%.2f) !")
                        % (paydict['paylines'][0].partner_id.name,
                           paydict['total']))
                vals = self._prepare_bank_payment_line(paydict['paylines'])
                bplo.create(vals)
        return res
