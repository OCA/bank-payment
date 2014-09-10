# -*- coding: utf-8 -*-
from openerp.osv import orm


class payment_order(orm.Model):
    _inherit = 'payment.order'

    def test_undo_done(self, cr, uid, ids, context=None):
        """
        Called from the workflow. Used to unset done state on
        payment orders that were reconciled with bank transfers
        which are being cancelled
        """
        for order in self.browse(cr, uid, ids, context=context):
            if order.payment_order_type == 'debit':
                for line in order.line_ids:
                    if line.storno:
                        return False
        return super(payment_order, self).test_undo_done(
            cr, uid, ids, context=context)
