# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import time
from types import SimpleNamespace
from unittest.mock import patch

from freezegun import freeze_time

from odoo import fields
from odoo.api import call_kw
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.auth_totp.models.totp import hotp
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

from ..models.account_payment_api_batch import PaymentApiResultUnknown
from ..wizard.account_payment_api_second_factor import LOCKOUT, MAX_FAILURES

SECRET = b"fictitious-secret-20"
WIZARD_PATH = (
    "odoo.addons.account_payment_order_api.wizard.account_payment_api_second_factor"
)


class FakeBank:
    """Bank answering as told by the test, recording the calls it receives."""

    def __init__(self):
        self.calls = []
        self.send_answer = "accepted"
        self.query_answer = {}

    def reserve(self, batch):
        self.calls.append("reserve")
        return "LOT-%s" % batch.id

    def send(self, batch):
        self.calls.append("send")
        if isinstance(self.send_answer, Exception):
            raise self.send_answer
        return {
            "lines": {
                line.id: {"state": self.send_answer, "bank_reference": "P%s" % line.id}
                for line in batch.line_ids
            }
        }

    def query(self, batch):
        self.calls.append("query")
        return {
            "lines": {
                line.id: self.query_answer.get(line.id) for line in batch.line_ids
            }
        }

    def cancel(self, batch, api_lines):
        self.calls.append("cancel")
        return {"lines": {line.id: {"state": "cancelled"} for line in api_lines}}


@tagged("-at_install", "post_install")
class TestPaymentOrderApi(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        mode_model = cls.env["account.payment.mode"]
        cls.provider_field = mode_model._fields["api_provider"]
        cls.provider_selection = cls.provider_field.selection
        cls.provider_field.selection = [("test", "Test Bank")]
        cls.mode = mode_model.create(
            {
                "name": "Test bank API",
                "company_id": cls.company_data["company"].id,
                "bank_account_link": "fixed",
                "fixed_journal_id": cls.company_data["default_journal_bank"].id,
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "api_provider": "test",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.provider_field.selection = cls.provider_selection
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        # The durable steps open their own cursor: share the test transaction.
        self.registry.enter_test_mode(self.cr)
        self.addCleanup(self.registry.leave_test_mode)
        self.bank = FakeBank()
        batch_class = type(self.env["account.payment.api.batch"])
        for operation in ("reserve", "send", "query", "cancel"):
            patcher = patch.object(
                batch_class,
                "_api_test_%s" % operation,
                create=True,
                new=lambda batch, *args, op=operation: getattr(self.bank, op)(
                    batch, *args
                ),
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        self.bills = self.env["account.move"]
        for amount in (100.0, 250.0):
            self.bills |= self.init_invoice(
                "in_invoice", amounts=[amount], post=True, partner=self.partner_a
            )
        self.order = self.env["account.payment.order"].create(
            {"payment_mode_id": self.mode.id, "payment_type": "outbound"}
        )
        self.payables = self.bills.line_ids.filtered(
            lambda x: x.account_id.account_type == "liability_payable"
        )
        self.payables.create_payment_line_from_move_line(self.order)
        for payline in self.order.payment_line_ids:
            payline.communication = payline.move_line_id.move_id.name
        self.order.draft2open()

    def _api_line(self, bill):
        return self.order.api_line_ids.filtered(
            lambda x: x.move_line_id.move_id == bill
        )

    def test_mode_refuses_grouped_lines(self):
        with self.assertRaises(ValidationError):
            self.mode.group_lines = True

    def test_no_payment_file(self):
        with self.assertRaises(UserError):
            self.order.open2generated()

    def test_send_reserves_first_and_posts_only_when_paid(self):
        self.assertEqual(len(self.order.payment_ids), 2)
        self.order.action_api_send()
        self.assertEqual(self.bank.calls, ["reserve", "send"])
        batch = self.order.api_batch_ids
        self.assertRecordValues(
            batch, [{"state": "sent", "bank_reference": "LOT-%s" % batch.id}]
        )
        self.assertEqual(self.order.api_state, "tracking")
        self.assertEqual(set(self.order.payment_ids.mapped("state")), {"draft"})
        with self.assertRaises(UserError):
            self.order.action_api_send()

        paid, refused = self._api_line(self.bills[0]), self._api_line(self.bills[1])
        self.bank.query_answer = {
            paid.id: {"state": "paid", "authentication": "AUTH1"},
            refused.id: {"state": "rejected", "reason": "295"},
        }
        self.env["account.payment.api.batch"]._cron_api_check()
        self.assertEqual(paid.payment_id.state, "posted")
        self.assertIn(self.bills[0].payment_state, ("in_payment", "paid"))
        self.assertEqual(refused.payment_id.state, "cancel")
        self.assertEqual(self.bills[1].payment_state, "not_paid")
        self.assertEqual(self.order.state, "uploaded")
        self.assertEqual(self.order.api_state, "done")

        # The rejected bill can go to a new order right away.
        wizard = (
            self.env["account.payment.line.create"]
            .with_context(active_model="account.payment.order", active_id=self.order.id)
            .create(
                {
                    "order_id": self.order.id,
                    "target_move": "posted",
                    "date_type": "move",
                    "payment_mode": "any",
                }
            )
        )
        proposed = self.env["account.move.line"].search(
            wizard._prepare_move_line_domain()
        )
        self.assertIn(refused.move_line_id, proposed)
        self.assertNotIn(paid.move_line_id, proposed)

    def test_failed_reservation_can_be_sent_again(self):
        reserve = self.bank.reserve
        self.bank.reserve = lambda batch: (_ for _ in ()).throw(UserError("bank down"))
        # Not assertRaises: its savepoint would also undo the batch, which the
        # dedicated cursor keeps in production.
        raised = False
        try:
            self.order.action_api_send()
        except UserError:
            raised = True
        self.assertTrue(raised)
        self.assertEqual(self.order.api_batch_ids.state, "draft")
        self.assertTrue(self.order.api_can_send)
        self.bank.reserve = reserve
        self.order.action_api_send()
        self.assertEqual(self.order.api_batch_ids.state, "sent")
        self.assertFalse(self.order.api_can_send)

    def test_unknown_outcome_is_checked_not_sent_again(self):
        self.bank.send_answer = PaymentApiResultUnknown("timeout")
        self.order.action_api_send()
        self.assertEqual(self.order.api_batch_ids.state, "uncertain")
        self.assertEqual(self.order.api_state, "sending")
        self.bank.query_answer = {
            line.id: {"state": "awaiting_release"} for line in self.order.api_line_ids
        }
        self.env["account.payment.api.batch"]._cron_api_check()
        self.assertEqual(self.bank.calls, ["reserve", "send", "query"])
        self.assertEqual(self.order.api_batch_ids.state, "sent")
        self.assertEqual(
            set(self.order.api_line_ids.mapped("state")), {"awaiting_release"}
        )

    @mute_logger(
        "odoo.addons.account_payment_order_api.models.account_payment_api_batch"
    )
    def test_failed_send_releases_the_bills(self):
        self.bank.send_answer = UserError("invalid account")
        self.order.action_api_send()
        self.assertEqual(self.order.api_batch_ids.state, "failed")
        self.assertEqual(set(self.order.api_line_ids.mapped("state")), {"refused"})
        self.assertEqual(set(self.order.payment_ids.mapped("state")), {"cancel"})
        self.assertEqual(self.order.state, "uploaded")

    def test_cancel_at_bank_and_cancel_order(self):
        self.order.action_api_send()
        with self.assertRaises(UserError):
            self.order.action_cancel()
        line = self._api_line(self.bills[0])
        line.action_api_cancel()
        self.assertEqual(line.state, "cancelled")
        self.assertEqual(line.payment_id.state, "cancel")
        with self.assertRaises(UserError):
            line.action_api_cancel()

    def test_returned_after_paid_reopens_the_bill(self):
        self.order.action_api_send()
        line = self._api_line(self.bills[0])
        line._api_apply({"state": "paid"})
        self.assertIn(self.bills[0].payment_state, ("in_payment", "paid"))
        line._api_apply({"state": "rejected"})
        self.assertEqual(line.state, "paid")
        line._api_apply({"state": "returned", "reason": "closed account"})
        self.assertEqual(line.payment_id.state, "cancel")
        self.assertEqual(self.bills[0].payment_state, "not_paid")

    # Second factor ---------------------------------------------------------

    def _enable_second_factor(self):
        self.mode.api_require_second_factor = True
        self._give_secret(self.env.user)
        self.session = SimpleNamespace(uid=self.env.uid)
        patcher = patch(f"{WIZARD_PATH}.request", SimpleNamespace(session=self.session))
        patcher.start()
        self.addCleanup(patcher.stop)

    def _give_secret(self, user):
        user.sudo().totp_secret = base64.b32encode(SECRET).decode()

    def _code(self, offset=0):
        return str(hotp(SECRET, int(time.time() / 30) + offset)).zfill(6)

    def _open(self, order=None):
        action = (order or self.order).action_api_send()
        self.assertEqual(action["res_model"], "account.payment.api.second.factor")
        return self.env[action["res_model"]].browse(action["res_id"])

    def _confirm(self, wizard, code):
        wizard.code = code
        self.env.flush_all()
        return wizard.action_confirm()

    def _refusal(self, wizard, code):
        # Not assertRaises: its savepoint would also undo the failure count, which
        # the dedicated cursor keeps in production.
        try:
            self._confirm(wizard, code)
        except UserError as error:
            return str(error)
        return self.fail("The code was accepted.")

    def test_second_factor_is_required_and_sends_once(self):
        self._enable_second_factor()
        self._open()
        self._open(self.order.with_context(second_factor_done=True, api_skip=True))
        call_kw(
            self.env["account.payment.order"], "action_api_send", [self.order.ids], {}
        )
        wizard = self._open()
        other = self._open()
        self.assertEqual(self.bank.calls, [])

        code = self._code()
        self._confirm(wizard, code)
        self.assertEqual(self.bank.calls, ["reserve", "send"])
        self.assertFalse(wizard.code)
        message = self.order.message_ids[0]
        self.assertEqual(message.author_id, self.env.user.partner_id)
        self.assertIn(self.env.user.name, message.body)
        self.assertNotIn(code, message.body)

        self.assertIn("already used", self._refusal(other, code))
        # A later code is good: only the order has nothing left to send.
        self.assertIn("nothing to send", self._refusal(other, self._code(1)))
        self.assertEqual(self.bank.calls, ["reserve", "send"])

    @mute_logger(WIZARD_PATH)
    def test_second_factor_wrong_codes_lock_out(self):
        self._enable_second_factor()
        wizard = self._open()
        good = {self._code(offset) for offset in (-1, 0, 1)}
        wrong = next(
            c for c in ("000000", "000001", "000002", "000003") if c not in good
        )
        for __ in range(MAX_FAILURES):
            self.assertIn("double-check", self._refusal(wizard, wrong))
        self.assertIn("Too many", self._refusal(wizard, self._code()))
        self.assertEqual(self.bank.calls, [])
        with freeze_time(fields.Datetime.now() + LOCKOUT):
            self._confirm(wizard, self._code())
        self.assertEqual(self.bank.calls, ["reserve", "send"])

    def test_second_factor_refusals_before_the_code(self):
        self._enable_second_factor()
        self.session.uid = False
        with self.assertRaisesRegex(UserError, "user session"):
            self.order.action_api_send()
        self.session.uid = self.env.uid
        wizard = self._open()
        self.env.user.sudo().totp_secret = False
        with self.assertRaisesRegex(UserError, "two-factor"):
            self.order.action_api_send()
        with self.assertRaisesRegex(UserError, "two-factor"):
            self._confirm(wizard, self._code())

        self._give_secret(self.env.user)
        for vals in (
            {"method": "unlink"},
            {"method": "_api_create_batches"},
            {"res_model": "res.users", "res_ids": self.env.user.ids},
            {"res_model": "no.such.model"},
        ):
            wizard.write(dict({"method": "_api_send_to_bank"}, **vals))
            with self.assertRaisesRegex(UserError, "cannot be confirmed"):
                self._confirm(wizard, self._code())
            wizard.write({"res_model": self.order._name, "res_ids": self.order.ids})
        self.assertEqual(self.bank.calls, [])
        state_model = self.env["account.payment.api.second.factor.state"]
        with self.assertRaises(AccessError):
            state_model.with_user(self.env.user).search([])

    def test_second_person_and_provider_action(self):
        self._enable_second_factor()
        batch_class = type(self.env["account.payment.api.batch"])
        authorized = []
        for name, value in (
            ("_api_second_factor_methods", ("_api_test_authorize",)),
            ("_api_test_authorize", lambda batch: authorized.append(batch)),
        ):
            patcher = patch.object(batch_class, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)
        factor = self.env["account.payment.api.second.factor"]
        self.order._api_create_batches()
        batch = self.order.api_batch_ids

        factor._run_after_check(batch, "_api_test_authorize", required=False)
        self.assertEqual(len(authorized), 1)
        wizard = factor.browse(
            factor._run_after_check(batch, "_api_test_authorize")["res_id"]
        )
        self.assertEqual(len(authorized), 1)

        self.order.company_id.api_second_person_required = True
        with self.assertRaises(AccessError):
            self.order.with_user(self.env.user).api_confirmed_user_id = self.env.ref(
                "base.user_admin"
            )
        with self.assertRaisesRegex(UserError, "second person"):
            self.order.action_api_send()
        with self.assertRaisesRegex(UserError, "second person"):
            self._confirm(wizard, self._code())
        self.assertEqual(len(authorized), 1)

        other = self.env.user.sudo().copy({"login": "second.person@example.com"})
        self._give_secret(other)
        self.session.uid = other.id
        wizard = factor.with_user(other).browse(
            factor.with_user(other)._run_after_check(
                batch.with_user(other), "_api_test_authorize"
            )["res_id"]
        )
        self._confirm(wizard, self._code())
        self.assertEqual(len(authorized), 2)
        self.assertEqual(self.bank.calls, [])
        self.assertEqual(self.order.message_ids[0].author_id, other.partner_id)

    def test_second_factor_settings_locked_after_confirmation(self):
        self.mode.api_require_second_factor = True
        no_factor = self.mode.copy(
            {"name": "No factor", "api_require_second_factor": False}
        )
        cash = self.company_data["default_journal_cash"]
        for vals in ({"payment_mode_id": no_factor.id}, {"journal_id": cash.id}):
            with self.assertRaisesRegex(UserError, "already confirmed"):
                self.order.write(vals)
        self.order.write({"payment_mode_id": self.mode.id})
        for vals in ({"api_require_second_factor": False}, {"api_provider": False}):
            with self.assertRaisesRegex(UserError, "still open"):
                self.mode.write(vals)

        self.order._api_send_to_bank()
        self.mode.api_require_second_factor = False
        with self.assertRaisesRegex(UserError, "still open"):
            self.mode.api_provider = False

        file_mode = no_factor.copy({"name": "File", "api_provider": False})
        file_order = self.env["account.payment.order"].create(
            {"payment_mode_id": file_mode.id, "payment_type": "outbound"}
        )
        file_order.payment_mode_id = no_factor
        file_order.payment_mode_id = file_mode
        file_order.state = "open"
        with self.assertRaisesRegex(UserError, "already confirmed"):
            file_order.payment_mode_id = no_factor
        file_order.journal_id = cash

    def test_direct_state_changes_keep_the_controls(self):
        self._enable_second_factor()
        self.order.company_id.api_second_person_required = True
        other = self.env.user.sudo().copy({"login": "second.person@example.com"})
        self._give_secret(other)
        self.session.uid = other.id
        order = self.order.with_user(other)
        order.write({"state": "draft"})
        self.assertFalse(self.order.sudo().api_confirmed_user_id)
        order.payment_line_ids[0].amount_currency = 1.0
        order.write({"state": "open"})
        self.assertEqual(self.order.sudo().api_confirmed_user_id, other)
        factor = self.env["account.payment.api.second.factor"]
        with self.assertRaisesRegex(UserError, "second person"):
            factor.with_user(other)._run_after_check(order, "_api_send_to_bank")

        self.session.uid = self.env.uid
        with self.assertRaisesRegex(UserError, "draft payment"):
            self.order.action_api_send()
        self.assertEqual(self.bank.calls, [])

        self.order.action_cancel()
        self.order.cancel2draft()
        self.order.draft2open()
        self.assertEqual(self.order.sudo().api_confirmed_user_id, self.env.user)
        self.session.uid = other.id
        wizard = factor.with_user(other).browse(order.action_api_send()["res_id"])
        self._confirm(wizard, self._code())
        self.assertEqual(self.bank.calls, ["reserve", "send"])
        self.assertEqual(self.order.payment_line_ids[0].payment_ids.amount, 1.0)
        with self.assertRaisesRegex(UserError, "already sent"):
            order.write({"state": "draft"})

    def test_payment_lines_locked_out_of_draft(self):
        line = self.order.payment_line_ids[0]
        calls = [
            lambda: line.write({"amount_currency": 1.0}),
            lambda: line.write({"partner_id": self.partner_b.id}),
            lambda: line.write({"communication": "other"}),
            lambda: line.copy({"order_id": self.order.id}),
            line.unlink,
        ]
        for call in calls:
            with self.assertRaisesRegex(UserError, "cannot change"):
                call()
        file_mode = self.mode.copy({"name": "File", "api_provider": False})
        file_order = self.env["account.payment.order"].create(
            {
                "payment_mode_id": file_mode.id,
                "payment_type": "outbound",
                "state": "open",
            }
        )
        draft_order = self.env["account.payment.order"].create(
            {"payment_mode_id": self.mode.id, "payment_type": "outbound"}
        )
        new_line = line.copy({"order_id": draft_order.id, "name": "New"})
        with self.assertRaisesRegex(UserError, "cannot change"):
            new_line.order_id = self.order
        new_line.order_id = file_order
        new_line.amount_currency = 1.0

    def _payment_user(self, groups="account_payment_order.group_account_payment"):
        return new_test_user(
            self.env,
            login=f"{groups}@example.com",
            groups="base.group_user,account.group_account_invoice," + groups,
            company_id=self.env.company.id,
            company_ids=[(6, 0, self.env.company.ids)],
        )

    def test_payment_user_sends_checks_and_cannot_touch_batches(self):
        order = self.order.with_user(self._payment_user())
        self.bank.send_answer = PaymentApiResultUnknown("timeout")
        order.action_api_send()
        batch = order.api_batch_ids
        self.assertEqual(batch.state, "uncertain")
        paid, rejected = batch.line_ids
        with self.assertRaises(AccessError):
            batch.state = "draft"
        with self.assertRaises(AccessError):
            paid.payment_line_id = rejected.payment_line_id
        with self.assertRaises(AccessError):
            self.env["account.payment.api.line"].with_user(order.env.user).create(
                {"batch_id": batch.id, "payment_line_id": paid.payment_line_id.id}
            )
        with self.assertRaisesRegex(UserError, "nothing to send"):
            order.action_api_send()
        self.assertEqual(self.bank.calls.count("send"), 1)

        self.bank.query_answer = {
            paid.id: {"state": "paid"},
            rejected.id: {"state": "rejected", "reason": "295"},
        }
        order.action_api_check()
        self.assertEqual(batch.state, "sent")
        self.assertEqual(rejected.payment_id.state, "cancel")
        self.assertEqual(rejected.move_line_id.move_id.payment_state, "not_paid")
        self.assertIn(paid.move_line_id.move_id.payment_state, ("in_payment", "paid"))
        self.assertEqual(order.state, "uploaded")

    def test_read_only_user_reaches_no_bank(self):
        reader = self.order.with_user(
            self._payment_user("account.group_account_readonly")
        )
        with self.assertRaises(AccessError):
            reader.action_api_send()
        self.order.action_api_send()
        calls = list(self.bank.calls)
        with self.assertRaises(AccessError):
            reader.action_api_check()
        with self.assertRaises(AccessError):
            reader.api_line_ids.action_api_cancel()
        self.assertEqual(self.bank.calls, calls)
