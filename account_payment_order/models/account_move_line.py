# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo import api, fields, models
from odoo.fields import first
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

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Empty partner bank for avoiding inconsistencies."""
        self.partner_bank_id = None

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
        partner_bank_id = self.partner_bank_id.id
        if not partner_bank_id:
            bank_ids = self.partner_id.bank_ids
            # trick this for making it compatible with partner_bank_active
            # forcing the search for discarding inactive records
            if 'active' in bank_ids:  # pragma: no cover
                bank_ids = bank_ids.filtered('active')
            partner_bank_id = first(bank_ids).id
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
            arch, fields = self.env['ir.ui.view'].postprocess_and_fields(
                self._name, doc, view_id,
            )
            result.update(arch=arch, fields=fields)
        return result

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Set payment orders with fully reconciled lines to done """
        result = super().reconcile(
            writeoff_acc_id=writeoff_acc_id,
            writeoff_journal_id=writeoff_journal_id,
        )
        if not self.env.context.get('account_payment_order_defer_close'):
            self.filtered('full_reconcile_id')._close_payment_orders()
        return result

    @api.multi
    def _close_payment_orders(self):
        """
        Set payment orders linked to move lines in self to done if all
        of them are reconciled
        """
        for order in self._find_payment_orders():
            if order.state != 'done' and order._all_lines_reconciled():
                order.action_done()

    @api.multi
    def _find_payment_orders(self):
        """
        Return all payment orders linked (directly by payment_line_ids
        or indirectly by reconciliation with a transfer account) to self
        """
        return self.mapped(
            'move_id.line_ids.bank_payment_line_id.order_id'
        ) | self.mapped(
            'full_reconcile_id.reconciled_line_ids.move_id.line_ids.'
            'bank_payment_line_id.order_id'
        )
