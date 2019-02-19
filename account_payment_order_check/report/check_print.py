from odoo import api, models


class ReportCheckPrint(models.AbstractModel):
    _inherit = 'report.account_check_printing_report_base.report_check_base'

    @api.multi
    def get_paid_lines(self, payments):
        if self.env.context.get('active_model') != 'bank.payment.line':
            return super().get_paid_lines(payments)
        res = {}
        for bank_line in payments:
            vals = []
            for line in bank_line.payment_line_ids:
                vals.append({
                    'date_due': line.ml_maturity_date,
                    'reference': line._get_check_reference(),
                    'number': line.move_line_id.invoice_id.name,
                    'amount_total': line.amount_currency,
                    'residual': line.amount_currency,
                    'paid_amount': 0.0
                })
            res[bank_line.id] = vals
        return res
