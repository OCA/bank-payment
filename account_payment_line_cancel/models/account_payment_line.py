# -*- coding: utf-8 -*-
# Copyright 2017 Compassion CH (http://www.compassion.ch)
# @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, _


class AccountCancelPayment(models.Model):
    _inherit = 'account.payment.line'

    cancel_reason = fields.Char()

    def cancel_line(self):
        """
         This method proceed to call private methods to remove payment lines
         from payment order

        A cancel reason can be put in the cancel_reason field.

        :return: True
        """
        # Retrieve all account_move_line(s) associated with the previous
        # account_payment_line(s).
        all_account_move_lines = self.mapped('move_line_id')
        # Add the message to the invoice and to the payment order
        self._post_cancel_message()
        # Unreconcile transfer journal entries
        full_reconcile_ids = all_account_move_lines.mapped(
            'full_reconcile_id.id')
        payment_orders = self.mapped('order_id')
        if full_reconcile_ids:
            # Retrieve the counterparts of the previous move_lines.
            # The counter part should always be unique.
            account_move_line_counterpart = self.env[
                'account.move.line'].search([
                    ('full_reconcile_id', 'in', full_reconcile_ids),
                    ('id', 'not in', all_account_move_lines.ids),
                    ('move_id.payment_order_id', 'in', payment_orders.ids)])

            # All the move lines with the same reconcile id are unreconciled.
            account_move_line_counterpart.remove_move_reconcile()
            # unpost and delete the moves from the journal.
            account_move_counterpart = account_move_line_counterpart.mapped(
                'move_id')
            account_move_counterpart.button_cancel()
            account_move_counterpart.unlink()

        # Remove bank.payment.line
        self.mapped('bank_line_id').with_context(force_unlink=True).unlink()

        # Search if there is something left in the payment order.
        for payment_order in payment_orders:
            other_lines = self.search_count([
                ('order_id', '=', payment_order.id),
                ('id', 'not in', self.ids)
            ])
            if not other_lines:
                payment_order.action_done_cancel()

        # Delete the payment line in the payment order.
        res = self.unlink()
        # Force recomputation of total
        payment_orders._compute_total()
        if self.env.context.get('cancel_line_from_payment_order'):
            # to see that the state of the order has changed, we need
            # to update the whole view. Do that only if necessary.
            res = {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        return res

    def _post_cancel_message(self):
        """
        This method is used to post message on the invoices that have been
        deleted from the payment order and it post a message too on the
        payment order for each deleted invoice.
        """
        for payment_line in self:
            cancel_reason = payment_line.cancel_reason or _(
                u"no reason given.")
            # Create a link to the invoice that was removed
            invoice = payment_line.move_line_id.invoice_id
            order = payment_line.order_id
            invoice_url = u'<a href="web#id={}&view_type=form&model=' \
                u'account.invoice">{}</a>'.format(invoice.id,
                                                  invoice.move_name)
            payment_order_url = u'<a href="web#id={}&view_type=form&model=' \
                u'account.payment.order">{}</a>'.format(order.id, order.name)
            # Add a message to the invoice
            invoice.message_post(
                _(u"The invoice has been removed from ") + u"{}, {}"
                .format(payment_order_url, cancel_reason)
            )
            # Add a message to the payment order
            payment_line.order_id.message_post(
                invoice_url + _(u" has been removed, ") + cancel_reason)
