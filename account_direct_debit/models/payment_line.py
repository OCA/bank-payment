# -*- coding: utf-8 -*-
from openerp import api, exceptions, models, fields, _, workflow


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    @api.multi
    def debit_storno(self, amount, currency, storno_retry=True):
        """The processing of a storno is triggered by a debit
        transfer on one of the company's bank accounts.
        This method offers to re-reconcile the original debit
        payment. For this purpose, we have registered that
        payment move on the payment line.

        Return the (now incomplete) reconcile id. The caller MUST
        re-reconcile this reconcile with the bank transfer and
        re-open the associated invoice.

        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :param boolean storno_retry: when True, attempt to reopen the invoice,
          set the invoice to 'Debit denied' otherwise.
        :return: an incomplete reconcile for the caller to fill
        :rtype: database id of an account.move.reconcile resource.
        """
        self.ensure_one()
        reconcile_obj = self.env['account.move.reconcile']
        line = self
        reconcile = reconcile_obj.browse([])
        if (line.transit_move_line_id and not line.storno and
            self.env['res.currency'].is_zero(
                currency, (
                    (line.transit_move_line_id.credit or 0.0) -
                    (line.transit_move_line_id.debit or 0.0) + amount))):
            # Two different cases, full and partial
            # Both cases differ subtly in the procedure to follow
            # Needs refractoring, but why is this not in the OpenERP API?
            # Actually, given the nature of a direct debit order and storno,
            # we should not need to take partial into account on the side of
            # the transit_move_line.
            if line.transit_move_line_id.reconcile_partial_id:
                reconcile_partial = \
                    line.transit_move_line_id.reconcile_partial_id
                reconcile = line.transit_move_line_id.reconcile_id
                if len(reconcile.line_partial_ids) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile_partial.write({
                        'line_id': [(6, 0, line.transit_move_line_id.id)],
                        'line_partial_ids': [(6, 0, [])]
                    })
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    reconcile_partial.write({
                        'line_partial_ids': [(3, line.transit_move_line_id.id)]
                    })
                    reconcile = reconcile_obj.create({
                        'type': 'auto',
                        'line_id': [(6, 0, line.transit_move_line_id.id)]
                    })
            elif line.transit_move_line_id.reconcile_id:
                reconcile = line.transit_move_line_id.reconcile_id
                if len(line.transit_move_line_id.reconcile_id.line_id) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile.write({
                        'line_id': [(6, 0, [line.transit_move_line_id.id])],
                    })
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    reconcile = line.transit_move_line_id.reconcile_id
                    partial_ids = [x.id for x in reconcile.line_id
                                   if x.id != line.transit_move_line_id.id]
                    reconcile.write({
                        'line_partial_ids': [(6, 0, partial_ids)],
                        'line_id': [(6, 0, [])],
                    })
                    reconcile = reconcile_obj.create({
                        'type': 'auto',
                        'line_id': [(6, 0, line.transit_move_line_id.id)]
                    })
            # mark the payment line for storno processed
            if reconcile:
                self.write({'storno': True})
                # put forth the invoice workflow
                if line.move_line_id.invoice:
                    activity = (storno_retry and 'open_test' or
                                'invoice_debit_denied')
                    workflow.trg_validate(
                        self.env.uid, 'account.invoice',
                        line.move_line_id.invoice.id, activity, self.env.cr)
        return reconcile.id

    @api.multi
    def get_storno_account_id(self, amount, currency):
        """Check the match of the arguments, and return the account associated
        with the storno.
        Used in account_banking interactive mode

        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :return: an account if there is a full match, False otherwise
        :rtype: database id of an account.account resource.
        """
        self.ensure_one()
        account_id = False
        if (self.transit_move_line_id and not self.storno and
            self.env['res.currency'].is_zero(
                currency, (
                    (self.transit_move_line_id.credit or 0.0) -
                    (self.transit_move_line_id.debit or 0.0) + amount))):
            account_id = self.transit_move_line_id.account_id.id
        return account_id

    @api.one
    def debit_reconcile(self):
        """Raise if a payment line is passed for which storno is True."""
        if self.storno:
            raise exceptions.except_orm(
                _('Can not reconcile'),
                _('Cancelation of payment line \'%s\' has already been '
                  'processed') % self.name)
        return super(PaymentLine, self).debit_reconcile()

    storno = fields.Boolean(
        'Storno', readonly=True,
        help="If this is true, the debit order has been canceled by the bank "
        "or by the customer")
