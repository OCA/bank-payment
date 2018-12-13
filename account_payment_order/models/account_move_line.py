# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo import models, fields, api
from odoo.osv import orm


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_bank_id = fields.Many2one(
        'res.partner.bank', string='Partner Bank Account',
        help='Bank account on which we should pay the supplier')
    bank_payment_line_id = fields.Many2one(
        'bank.payment.line', string='Bank Payment Line',
        readonly=True)
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
        partner_bank_id = False
        if not self.partner_bank_id:
            # Select partner bank account automatically if there is only one
            if len(self.partner_id.bank_ids) == 1:
                partner_bank_id = self.partner_id.bank_ids[0].id
        else:
            partner_bank_id = self.partner_bank_id.id
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
        aplo = self.env['account.payment.line']
        for mline in self:
            aplo.create(mline._prepare_payment_line_vals(payment_order))
        return

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
