- Webhooks: banks that notify status changes could update the lines without
  waiting for the scheduled check; providers can call the same update today.
- Releasing a batch from Odoo, for banks that allow it through the API.
- A provider must raise `PaymentApiResultUnknown` whenever the bank may have
  received a batch (timeout, connection lost); any other error marks the lines
  as refused.
- A provider action that moves money can require the same code: list its private
  method in `_api_second_factor_methods` on the model and return
  `self.env["account.payment.api.second.factor"]._run_after_check(self, method)`.
