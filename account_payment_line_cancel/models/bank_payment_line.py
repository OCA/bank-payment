from odoo import api, models, _
from odoo.exceptions import UserError

from odoo.addons.account_payment_order.models.bank_payment_line \
    import BankPaymentLine


class APLCBankPaymentLine(models.Model):
    _inherit = "bank.payment.line"

    @api.multi
    def unlink(self):
        if not self.env.context.get('force_unlink'):
            for line in self:
                order_state = line.order_id.state
                if order_state == 'uploaded':
                    raise UserError(_(
                        "Cannot delete a payment order line whose payment "
                        "order is in state '{}'. You need to cancel it "
                        "first.").format(order_state))
        return super(BankPaymentLine, self).unlink()
