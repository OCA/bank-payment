# -*- coding: utf-8 -*-
# Copyright 2020 Compassion Suisse (http://www.compassion.ch)
# @author: David Wulliamoz, Emanuel Cino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    def free_line(self):
        """
        Set move_line_id to Null in order to cancel the related invoice
        check if the payment_line is returned, if not, check the related
        move_line is not reconciled
        """
        for rec in self:
            if not rec.move_line_id.full_reconcile_id:
                rec._post_free_message()
                rec.move_line_id = False
                rec.payment_line_returned = True

            else:
                raise exceptions.UserError(
                    "Payment is reconciled and cannot be cancelled.")

    def _post_free_message(self):
        """
        post message on the invoice that have been freed from the payment order
        post message on the payment order for each payment_line unlinked from the move_line.
        """
        for payment_line in self:
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
                body="The invoice has been marked as returned and freed from "
                + payment_order_url
            )
            # Add a message to the payment order
            payment_line.order_id.message_post(
                body=invoice_url + " has been unlinked from the line: "
                + payment_line.name)
