/** @odoo-module */
/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ListRenderer} from "@web/views/list/list_renderer";
import {PaymentScheduleDashboard} from "@account_payment_schedule/views/payment_schedule_dashboard.esm";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export class PaymentScheduleListRenderer extends ListRenderer {}

PaymentScheduleListRenderer.template = "account_payment_schedule.ListRenderer";
PaymentScheduleListRenderer.components = {
    ...ListRenderer.components,
    PaymentScheduleDashboard,
};

export const paymentScheduleListView = {
    ...listView,
    Renderer: PaymentScheduleListRenderer,
};

registry.category("views").add("payment_schedule_list", paymentScheduleListView);
