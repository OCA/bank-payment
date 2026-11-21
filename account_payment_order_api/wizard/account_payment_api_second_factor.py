# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
import re
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.auth_totp.models.totp import TOTP

_logger = logging.getLogger(__name__)

MAX_FAILURES = 5
LOCKOUT = timedelta(minutes=15)


class AccountPaymentApiSecondFactor(models.TransientModel):
    _name = "account.payment.api.second.factor"
    _description = "Second Factor for a Bank API Action"

    res_model = fields.Char(required=True, readonly=True)
    res_ids = fields.Json(required=True, readonly=True)
    method = fields.Char(required=True, readonly=True)
    description = fields.Char(string="Authorizes", readonly=True)
    code = fields.Char(string="Authenticator Code", copy=False)

    @api.model
    def _run_after_check(self, records, method, required=True):
        """Run the private ``method`` of ``records``, after the code when required.

        The model of ``records`` lists ``method`` in its class attribute
        ``_api_second_factor_methods`` and implements
        ``_api_second_factor_orders()``, which returns the payment orders involved.
        """
        if not required:
            return getattr(records, method)()
        wizard = self.create(
            {
                "res_model": records._name,
                "res_ids": records.ids,
                "method": method,
                "description": ", ".join(records.mapped("display_name")),
            }
        )
        wizard._api_check_can_run()
        return {
            "type": "ir.actions.act_window",
            "name": _("Confirm with Your Authenticator"),
            "res_model": self._name,
            "res_id": wizard.id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
        }

    def action_confirm(self):
        self.ensure_one()
        records = self._api_check_can_run()
        self._api_verify_code(records)
        return getattr(records, self.method)()

    def _api_check_can_run(self):
        """Everything but the code. A client can write any value on this wizard."""
        self.ensure_one()
        model_class = self.env.registry.get(self.res_model)
        allowed = {
            name
            for cls in (model_class.mro() if model_class else ())
            for name in vars(cls).get("_api_second_factor_methods", ())
        }
        records = (
            self.env[self.res_model].browse(self.res_ids).exists()
            if self.method in allowed
            else None
        )
        if not records:
            raise UserError(_("This action cannot be confirmed with a second factor."))
        user = self.env.user
        if not request or request.session.uid != user.id:
            raise UserError(_("This action can only be confirmed in a user session."))
        if not user.totp_enabled:
            raise UserError(
                _(
                    "This action requires two-factor authentication: enable it in "
                    "the Account Security tab of your user profile."
                )
            )
        for order in records._api_second_factor_orders():
            confirmed_by = order.sudo().api_confirmed_user_id
            if order.company_id.api_second_person_required and (
                not confirmed_by or confirmed_by == user
            ):
                raise UserError(
                    _(
                        "Payment order %(order)s needs a second person: the code "
                        "must be entered by a user other than the one who confirmed "
                        "the order (%(user)s).",
                        order=order.name,
                        user=confirmed_by.name or _("unknown"),
                    )
                )
        return records

    def _api_verify_code(self, records):
        """Check the code in a dedicated cursor: the lockout, the used code and the
        audit message survive whatever happens to the transaction of the action."""
        code = re.sub(r"\s", "", self.code or "")
        uid = self.env.uid
        with self.env.registry.cursor() as cr:
            env = self.env(cr=cr, su=True)
            cr.execute(
                """
                INSERT INTO account_payment_api_second_factor_state
                    (user_id, failures, last_counter)
                VALUES (%s, 0, 0)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (uid,),
            )
            cr.execute(
                """
                SELECT id FROM account_payment_api_second_factor_state
                WHERE user_id = %s FOR UPDATE
                """,
                (uid,),
            )
            state = env["account.payment.api.second.factor.state"].browse(
                cr.fetchone()[0]
            )
            error = self._api_check_code(env.user, state, code)
            if not error:
                for order in records.with_env(env)._api_second_factor_orders():
                    order.message_post(
                        body=_(
                            "Second factor confirmed by %(user)s for %(method)s.",
                            user=env.user.name,
                            method=self.method,
                        ),
                        author_id=env.user.partner_id.id,
                        subtype_xmlid="mail.mt_note",
                    )
            self.with_env(env).code = False
        self.env.invalidate_all()
        if error:
            raise UserError(error)

    @api.model
    def _api_check_code(self, user, state, code):
        """Update ``state`` and return why the code is refused, if it is."""
        now = fields.Datetime.now()
        if state.failures >= MAX_FAILURES and now - state.last_failure < LOCKOUT:
            _logger.warning(
                "Bank API 2FA check: IGNORED for %s %r, on lockout", user, user.login
            )
            return _("Too many wrong codes: wait a few minutes and try again.")
        counter = None
        if re.fullmatch(r"\d{6}", code):
            key = base64.b32decode(user.totp_secret)
            counter = TOTP(key).match(int(code))
        if counter is None:
            _logger.info("Bank API 2FA check: FAIL for %s %r", user, user.login)
            state.write({"failures": state.failures + 1, "last_failure": now})
            return _("Verification failed, please double-check the 6-digit code.")
        if counter <= state.last_counter:
            _logger.info("Bank API 2FA check: REUSED for %s %r", user, user.login)
            return _("This code was already used: wait for the next one.")
        _logger.info("Bank API 2FA check: SUCCESS for %s %r", user, user.login)
        state.write({"failures": 0, "last_counter": counter})
        return False
