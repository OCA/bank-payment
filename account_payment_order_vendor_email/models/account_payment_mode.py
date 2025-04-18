# Copyright (C) 2020 Open Source Integrators
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, fields, models


class PaymentModeCustom(models.Model):
    _inherit = "account.payment.mode"

    send_email_to_partner = fields.Boolean(
        string="Send Email to Partner", default=False
    )
    email_temp_id = fields.Many2one(
        "mail.template",
        string="Email Template",
    )


class PaymentOrder(models.Model):
    _inherit = "account.payment.order"

    def send_vendor_email(self):
        context = dict(self._context)
        for rec in self:
            if rec.payment_mode_id.send_email_to_partner:
                date_generated = rec.date_generated
                for payment in rec.payment_ids:
                    partner_name = payment.partner_id.name
                    total_amount = payment.amount
                    payment_ref = payment.payment_reference
                    line_data = []
                    header_data = {
                        "inv_no": "Invoice No.",
                        "payment_amount": "Payment (in dollars)",
                        "discount": "Discount (in dollars)",
                        "inv_date": "Invoice Date",
                        "credit_ref": "Credit ref#",
                        "supp_inv": "Supp. Invoice#",
                        "inv_amount": "Invoice Amount",
                        "credit_amount": "Credit Amount",
                        "due_amount": "Due Amount",
                    }
                    line_data.append(header_data)
                    for payment_line in payment.payment_line_ids:
                        invoice_date = (
                            payment_line.move_line_id.move_id.invoice_date
                            and datetime.strftime(
                                payment_line.move_line_id.move_id.invoice_date,
                                "%Y/%m/%d",
                            )
                            or ""
                        )
                        line_dict = {
                            "inv_no": payment_line.move_line_id.move_id.name or "",
                            "payment_amount": payment_line.amount_currency,
                            "discount": payment_line.discount_amount,
                            "inv_date": invoice_date or "",
                            "credit_ref": payment_line.order_id.name,
                            "supp_inv": payment_line.move_line_id.move_id.name or "",
                            "inv_amount": payment_line.move_line_id.move_id.amount_total,
                            "credit_amount": payment_line.move_line_id.move_id.amount_untaxed,
                            "due_amount": payment_line.move_line_id.move_id.amount_residual,
                        }
                        line_data.append(line_dict)
                    template = rec.payment_mode_id.email_temp_id
                    if not template:
                        template = self.env.ref(
                            "account_payment_order_vendor_email."
                            "ach_payment_email_template"
                        )
                    partner_email_id = payment.partner_id.email
                    if partner_email_id:
                        template.write({"email_to": partner_email_id})
                        context.update(
                            {
                                "date": date_generated,
                                "partner_name": partner_name,
                                "total_amount": total_amount,
                                "payment_ref": payment_ref,
                                "line_data": line_data,
                            }
                        )
                        template.with_context(**context).send_mail(
                            rec.id, force_send=True
                        )
                        rec.message_post(
                            body=_("An email is not able to send to %s vendor.")
                            % partner_name
                        )
                    else:
                        rec.message_post(
                            body=_("An email is not able to send to %s vendor.")
                            % partner_name
                        )

    def generated2uploaded(self):
        res = super(PaymentOrder, self).generated2uploaded()
        if self.payment_mode_id.send_email_to_partner:
            self.send_vendor_email()
        return res


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    discount_amount = fields.Monetary(currency_field="currency_id")
