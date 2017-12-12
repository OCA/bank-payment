# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Marco Monzione <marco.mon@windowslive.com>, Emanuel Cino
#
#    The licence is in the file __manifest__.py
#
##############################################################################
from odoo import models


class AccountCancelPayment(models.AbstractModel):
    _name = 'account.payment.cancel'

    def cancel_payment(self, payment_order, bank_payment_line,
                       data_supp):
        """
         This method proceed to call private methods to remove payment
         from payment order

        :param payment_order: The order where to remove the payment
        :param bank_payment_line: The payment to remove
        :param data_supp: additional information used in the message
        :return: -
        """

        if payment_order and bank_payment_line:
            # Retrieve all account_payment_line associated to the
            # current bank_payment_line
            account_payment_lines = self.env['account.payment.line'].search(
                [('bank_line_id', '=', bank_payment_line.id)])

            if account_payment_lines:
                self._process_invoice_remove(
                    account_payment_lines, payment_order, data_supp)

    def _process_invoice_remove(self, account_payment_lines, payment_order,
                                data_supp):
        """
        This method unreconcile the given move lines and remove the payment.

        :param account_payment_lines: The payment to remove
        :param payment_order: The payment order where to remove the payment
        :param data_supp: additional information used in the message
        :return: -
        """

        # Retrieve all account_move_line(s) associated with the previous
        # account_payment_line(s).
        all_account_move_lines = account_payment_lines.mapped(
            'move_line_id')

        full_reconcile_id = all_account_move_lines.mapped(
            'full_reconcile_id').id

        if full_reconcile_id:
            # Retrieve the counterpart of the previous move_line(s).
            # The counter parth should always be unique.
            account_move_line_counterpart = self.env['account.move.line'].\
                search([('full_reconcile_id', '=', full_reconcile_id),
                        ('id', 'not in', all_account_move_lines.ids)], limit=1)

            # Keep only the move lines that belong to the desired payment order
            filtered_move_lines_counterpart = account_move_line_counterpart.\
                filtered(lambda l: l.move_id.payment_order_id == payment_order)

            account_move_counterpart = filtered_move_lines_counterpart.move_id
            # All the move lines with the same reconcile id are unreconciled.
            filtered_move_lines_counterpart.remove_move_reconcile()

            # unpost and delete the move from the journal.
            account_move_counterpart.button_cancel()
            account_move_counterpart.unlink()

        # Delete the payment line in the payment order.
        account_payment_lines.unlink()

        # Search if there is something left in the payment order.
        account_payment_line = self.env['account.payment.line'].search(
            [('order_id', '=', payment_order.id)])
        if len(account_payment_line) == 0 and \
                payment_order.state == 'uploaded':

                payment_order.action_done_cancel()

        # Add the message to the invoice and to the payment order
        self._post_message(data_supp, all_account_move_lines, payment_order)

    def _post_message(self, data_supp, account_move_lines, payment_order):
        """
        This method is used to post message on the invoices that have been
        deleted from the payment order and it post a message too on the
        payment order for each deleted invoice.

        :param data_supp: additional information used in the message
        :param account_move_lines: used to find the invoices where to post
        the message
        :param payment_order: used to post the message for each
        deleted invoices
        :return: -
        """
        for account_move_line in account_move_lines:

            # Create a link to the invoice that was removed
            url = '<a href="web#id={}&view_type=form&model=' \
                  'account.invoice">{}</a>'. \
                format(account_move_line.invoice_id.id,
                       account_move_line.invoice_id.move_name)

            if data_supp and 'add_tl_inf' in data_supp:

                # Add a message to the invoice
                account_move_line.invoice_id.message_post(
                    "The invoice has been removed from the payment "
                    "order because: " +
                    data_supp['add_tl_inf'])
                # Add a message to the payment order
                payment_order.message_post(
                    url + " has been removed because : " + data_supp[
                        'add_tl_inf'])
            else:
                # Add a message to the invoice
                account_move_line.invoice_id.message_post(
                    "The invoice has been removed from the payment order,"
                    " no reason given.")
                # Add a message to the payment order
                payment_order.message_post(
                    url + " has been removed no reason given.")
