/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {EventBus, useSubEnv} from "@odoo/owl";
import {ListController} from "@web/views/list/list_controller";
import {ListRenderer} from "@web/views/list/list_renderer";
import {PaymentScheduleDashboard} from "@account_payment_schedule/views/payment_schedule_dashboard.esm";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";

export class PaymentScheduleListController extends ListController {
    setup() {
        // The counters reload when the list reloads (filters, actions, new
        // orders) and when edited items are saved.
        this.paymentScheduleBus = new EventBus();
        useSubEnv({paymentScheduleBus: this.paymentScheduleBus});
        super.setup();
    }

    get modelParams() {
        const params = super.modelParams;
        const reload = () => this.paymentScheduleBus.trigger("reload");
        params.hooks = {...params.hooks, onRootLoaded: reload, onSavedMulti: reload};
        return params;
    }

    async onRecordSaved() {
        await super.onRecordSaved(...arguments);
        this.paymentScheduleBus.trigger("reload");
    }
}

export class PaymentScheduleListRenderer extends ListRenderer {
    static template = "account_payment_schedule.ListRenderer";
    static components = {...ListRenderer.components, PaymentScheduleDashboard};
}

export const paymentScheduleListView = {
    ...listView,
    Controller: PaymentScheduleListController,
    Renderer: PaymentScheduleListRenderer,
};

registry.category("views").add("payment_schedule_list", paymentScheduleListView);
