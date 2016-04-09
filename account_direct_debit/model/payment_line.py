# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
import netsvc
from tools.translate import _


class payment_line(orm.Model):
    _inherit = 'payment.line'

    def debit_storno(self, cr, uid, payment_line_id, amount,
                     currency, storno_retry=True, context=None):
        """
        The processing of a storno is triggered by a debit
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
        :param boolean storno_retry: when True, attempt to reopen the \
        invoice, set the invoice to 'Debit denied' otherwise.
        :return: an incomplete reconcile for the caller to fill
        :rtype: database id of an account.move.reconcile resource.
        """

        reconcile_obj = self.pool.get('account.move.reconcile')
        line = self.browse(cr, uid, payment_line_id)
        transit_move_line = line.transit_move_line_id
        reconcile_id = False
        if (line.transit_move_line_id and not line.storno and
            self.pool.get('res.currency').is_zero(
                cr, uid, currency, (
                    (line.transit_move_line_id.credit or 0.0) -
                    (line.transit_move_line_id.debit or 0.0) + amount))):
            # Two different cases, full and partial
            # Both cases differ subtly in the procedure to follow
            # Needs refractoring, but why is this not in the OpenERP API?
            # Actually, given the nature of a direct debit order and storno,
            # we should not need to take partial into account on the side of
            # the transit_move_line.
            if transit_move_line.reconcile_partial_id:
                reconcile_id = transit_move_line.reconcile_partial_id.id
                if len(transit_move_line.reconcile_id.line_partial_ids) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id,
                        {
                            'line_id': [(6, 0, transit_move_line.id)],
                            'line_partial_ids': [(6, 0, [])],
                        },
                        context=context)
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id,
                        {
                            'line_partial_ids': [(3, transit_move_line.id)],
                        },
                        context=context)
                    reconcile_id = reconcile_obj.create(
                        cr, uid,
                        {
                            'type': 'auto',
                            'line_id': [(6, 0, transit_move_line.id)],
                        },
                        context=context)
            elif transit_move_line.reconcile_id:
                reconcile_id = transit_move_line.reconcile_id.id
                if len(transit_move_line.reconcile_id.line_id) == 2:
                    # reuse the simple reconcile for the storno transfer
                    reconcile_obj.write(
                        cr, uid, reconcile_id,
                        {
                            'line_id': [(6, 0, [transit_move_line.id])]
                        },
                        context=context)
                else:
                    # split up the original reconcile in a partial one
                    # and a new one for reconciling the storno transfer
                    partial_ids = [
                        x.id for x in transit_move_line.reconcile_id.line_id
                        if x.id != transit_move_line.id
                    ]
                    reconcile_obj.write(
                        cr, uid, reconcile_id,
                        {
                            'line_partial_ids': [(6, 0, partial_ids)],
                            'line_id': [(6, 0, [])],
                        },
                        context=context)
                    reconcile_id = reconcile_obj.create(
                        cr, uid,
                        {
                            'type': 'auto',
                            'line_id': [(6, 0, transit_move_line.id)],
                        },
                        context=context)
            # mark the payment line for storno processed
            if reconcile_id:
                self.write(cr, uid, [payment_line_id],
                           {'storno': True}, context=context)
                # put forth the invoice workflow
                if line.move_line_id.invoice:
                    activity = (storno_retry and 'open_test' or
                                'invoice_debit_denied')
                    netsvc.LocalService("workflow").trg_validate(
                        uid, 'account.invoice', line.move_line_id.invoice.id,
                        activity, cr)
        return reconcile_id

    def get_storno_account_id(self, cr, uid, payment_line_id, amount,
                              currency, context=None):
        """
        Check the match of the arguments, and return the account associated
        with the storno.
        Used in account_banking interactive mode

        :param payment_line_id: the single payment line id
        :param amount: the (signed) amount debited from the bank account
        :param currency: the bank account's currency *browse object*
        :return: an account if there is a full match, False otherwise
        :rtype: database id of an account.account resource.
        """

        line = self.browse(cr, uid, payment_line_id)
        account_id = False
        if (line.transit_move_line_id and not line.storno and
            self.pool.get('res.currency').is_zero(
                cr, uid, currency, (
                    (line.transit_move_line_id.credit or 0.0) -
                    (line.transit_move_line_id.debit or 0.0) + amount))):
            account_id = line.transit_move_line_id.account_id.id
        return account_id

    def debit_reconcile(self, cr, uid, payment_line_id, context=None):
        """
        Raise if a payment line is passed for which storno is True
        """
        if isinstance(payment_line_id, (list, tuple)):
            payment_line_id = payment_line_id[0]
        payment_line_vals = self.read(
            cr, uid, payment_line_id, ['storno', 'name'], context=context)
        if payment_line_vals['storno']:
            raise orm.except_orm(
                _('Can not reconcile'),
                _('Cancelation of payment line \'%s\' has already been '
                  'processed') % payment_line_vals['name'])
        return super(payment_line, self).debit_reconcile(
            cr, uid, payment_line_id, context=context)

    _columns = {
        'storno': fields.boolean(
            'Storno',
            readonly=True,
            help=("If this is true, the debit order has been canceled "
                  "by the bank or by the customer")),
    }
