/** @odoo-module */
/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {PaymentScheduleCashflow} from "@account_payment_schedule/views/payment_schedule_cashflow.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(PaymentScheduleCashflow.prototype, "account_payment_schedule_priority", {
    setup() {
        this._super(...arguments);
        this.action = useService("action");
    },

    async onReplan() {
        const action = await this.orm.call(
            "account.move.line",
            "action_payment_schedule_replan",
            []
        );
        await this.action.doAction(action, {
            onClose: () => this.env.searchModel.search(),
        });
    },
});
