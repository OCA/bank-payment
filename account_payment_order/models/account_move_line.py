# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo import api, fields, models, _
from odoo.fields import first
from odoo.exceptions import UserError
from odoo.osv import orm


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account',
        help='Bank account on which we should pay the supplier')
    bank_payment_line_id = fields.Many2one(
        'bank.payment.line', string='Bank Payment Line',
        readonly=True,
        index=True,
    )
    payment_line_ids = fields.One2many(
        comodel_name='account.payment.line',
        inverse_name='move_line_id',
        string="Payment lines",
    )

    @api.multi
    def _prepare_payment_line_vals(self, payment_order):
        self.ensure_one()
        assert payment_order, 'Missing payment order'
        aplo = self.env['account.payment.line']
        # default values for communication_type and communication
        communication_type = 'normal'
        communication = self.move_id.ref or self.move_id.name
        # change these default values if move line is linked to an invoice
        if self.invoice_id:
            if self.invoice_id.reference_type != 'none':
                communication = self.invoice_id.reference
                ref2comm_type =\
                    aplo.invoice_reference_type2communication_type()
                communication_type =\
                    ref2comm_type[self.invoice_id.reference_type]
            else:
                if (
                        self.invoice_id.type in ('in_invoice', 'in_refund') and
                        self.invoice_id.reference):
                    communication = self.invoice_id.reference
                elif 'out' in self.invoice_id.type:
                    # Force to only put invoice number here
                    communication = self.invoice_id.number
        if self.currency_id:
            currency_id = self.currency_id.id
            amount_currency = self.amount_residual_currency
        else:
            currency_id = self.company_id.currency_id.id
            amount_currency = self.amount_residual
            # TODO : check that self.amount_residual_currency is 0
            # in this case
        if payment_order.payment_type == 'outbound':
            amount_currency *= -1
        partner_bank_id = self.partner_bank_id.id or first(
            self.partner_id.bank_ids).id
        vals = {
            'order_id': payment_order.id,
            'partner_bank_id': partner_bank_id,
            'partner_id': self.partner_id.id,
            'move_line_id': self.id,
            'communication': communication,
            'communication_type': communication_type,
            'currency_id': currency_id,
            'amount_currency': amount_currency,
            # date is set when the user confirms the payment order
            }
        return vals

    @api.multi
    def create_payment_line_from_move_line(self, payment_order):
        vals_list = []
        for mline in self:
            vals_list.append(mline._prepare_payment_line_vals(payment_order))
        return self.env['account.payment.line'].create(vals_list)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        # When the user looks for open payables or receivables, in the
        # context of payment orders, she should focus primarily on amount that
        # is due to be paid, and secondarily on the total amount. In this
        # method we are forcing to display both the amount due in company and
        # in the invoice currency.
        # We then hide the fields debit and credit, because they add no value.
        result = super(AccountMoveLine, self).fields_view_get(view_id,
                                                              view_type,
                                                              toolbar=toolbar,
                                                              submenu=submenu)

        doc = etree.XML(result['arch'])
        if view_type == 'tree' and self._module == 'account_payment_order':
            if not doc.xpath("//field[@name='balance']"):
                for placeholder in doc.xpath(
                        "//field[@name='amount_currency']"):
                    elem = etree.Element(
                        'field', {
                            'name': 'balance',
                            'readonly': 'True'
                        })
                    orm.setup_modifiers(elem)
                    placeholder.addprevious(elem)
            if not doc.xpath("//field[@name='amount_residual_currency']"):
                for placeholder in doc.xpath(
                        "//field[@name='amount_currency']"):
                    elem = etree.Element(
                        'field', {
                            'name': 'amount_residual_currency',
                            'readonly': 'True'
                        })
                    orm.setup_modifiers(elem)
                    placeholder.addnext(elem)
            if not doc.xpath("//field[@name='amount_residual']"):
                for placeholder in doc.xpath(
                        "//field[@name='amount_currency']"):
                    elem = etree.Element(
                        'field', {
                            'name': 'amount_residual',
                            'readonly': 'True'
                        })
                    orm.setup_modifiers(elem)
                    placeholder.addnext(elem)
            # Remove credit and debit data - which is irrelevant in this case
            for elem in doc.xpath("//field[@name='debit']"):
                doc.remove(elem)
            for elem in doc.xpath("//field[@name='credit']"):
                doc.remove(elem)
            result['arch'] = etree.tostring(doc)
        return result

    @api.multi
    def _prepare_new_payment_order(self, payment_mode=None):
        self.ensure_one()
        if payment_mode is None:
            payment_mode = self.env['account.payment.mode']
        vals = {
            'payment_mode_id': payment_mode.id or self.payment_mode_id.id,
        }
        # other important fields are set by the inherit of create
        # in account_payment_order.py
        return vals

    def action_add_to_payment_order(self):
        """
        Adds paymnet lines related to a move line not yet reconciled to a draft
        payment order
        :return: Action: Draft payment order
        """

        apoo = self.env['account.payment.order']
        result_payorder_ids = []
        result_count_lines = []
        action_payment_type = 'debit'
        for line_id in self:
            if line_id.reconciled:
                raise UserError(_(
                    "The move line %s is already reconciled") % line_id.ref)

            applicable_lines = line_id.filtered(
                lambda x: (
                    not x.reconciled and x.payment_mode_id.payment_order_ok and
                    x.account_id.internal_type in ('receivable', 'payable') and
                    not any(p_state in ('draft', 'open', 'generated')
                            for p_state in x.payment_line_ids.mapped('state'))
                )
            )
            if not applicable_lines:
                raise UserError(_(
                    'No Payment Line created for move line %s because '
                    'it already exists or because this move line is '
                    'already reconciled.') % line_id.ref)
            payment_modes = applicable_lines.mapped('payment_mode_id')
            if not payment_modes:
                raise UserError(_(
                    "No Payment Mode on move line %s") % line_id.ref)
            for payment_mode in payment_modes:
                payorder = apoo.search([
                    ('payment_mode_id', '=', payment_mode.id),
                    ('state', '=', 'draft')
                ], limit=1)
                new_payorder = False
                if not payorder:
                    payorder = apoo.create(line_id._prepare_new_payment_order(
                        payment_mode
                    ))
                    new_payorder = True
                result_payorder_ids.append(payorder)
                action_payment_type = payorder.payment_type
                count = 0
                for line in applicable_lines.filtered(
                    lambda x: x.payment_mode_id == payment_mode
                ):
                    line.create_payment_line_from_move_line(payorder)
                    count += 1
                result_count_lines.append((count, new_payorder))

        result_payorder_ids = list(set(result_payorder_ids))
        for payorder in range(len(result_payorder_ids)):
            count = result_count_lines[payorder][0]
            new_payorder = result_count_lines[payorder][1]
            payorder_id = result_payorder_ids[payorder]
            if new_payorder:
                line_id.invoice_id.message_post(
                    body=_(
                        '%d payment lines added to the new draft payment order'
                        ' %s which has been automatically created.'
                    ) % (count, payorder_id.name)
                )
            else:
                line_id.invoice_id.message_post(body=_(
                    '%d payment lines added to the existing draft '
                    'payment order %s.') % (count, payorder_id.name))
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account_payment_order',
            'account_payment_order_%s_action' % action_payment_type
        )
        if len(result_payorder_ids) == 1:
            action.update({
                'view_mode': 'form,tree,pivot,graph',
                'res_id': payorder_id.id,
                'views': False,
            })
        else:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'domain': "[('id', 'in', %s)]" % [
                    payment.id for payment in result_payorder_ids],
                'views': False,
            })
        return action

    def action_cancel_payment_line(self):
        """
        Removes payment lines related to move line that is still in draft
        payment order
        """
        open_aml = self.filtered(lambda x: x.payment_line_ids.state == "draft")
        open_aml.mapped('payment_line_ids').unlink()

        not_open_aml = self - open_aml
        if not_open_aml:
            payorder = not_open_aml.mapped(
                "payment_line_ids").mapped("order_id")
            raise UserError(
                _('The move line is related to payment order %s which is in '
                  'state %s' % (payorder.name, payorder.state)))
