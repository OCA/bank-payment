/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, onWillStart, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {KeepLast} from "@web/core/utils/concurrency";
import {PaymentScheduleCashflow} from "@account_payment_schedule/views/payment_schedule_cashflow.esm";
import {formatMonetary} from "@web/views/fields/formatters";

const GROUP_BY_TYPES = ["groupBy", "dateGroupBy"];

export class PaymentScheduleDashboard extends Component {
    static template = "account_payment_schedule.Dashboard";
    static props = {};
    static components = {PaymentScheduleCashflow};

    setup() {
        this.orm = useService("orm");
        this.keepLast = new KeepLast();
        this.state = useState({counters: [], currency_id: false});
        onWillStart(() => this.load());
        // Reload after every change of the list: edits, new orders, other filters.
        useBus(this.env.paymentScheduleBus, "reload", () => this.load());
    }

    async load() {
        const data = await this.keepLast.add(
            this.orm.call("account.move.line", "retrieve_payment_schedule_dashboard", [
                this.env.searchModel.globalDomain,
            ])
        );
        Object.assign(this.state, data);
    }

    getFilter(name) {
        return this.env.searchModel.getSearchItems((item) => item.name === name)[0];
    }

    isActive(counter) {
        const filter = this.getFilter(counter.filter);
        return Boolean(
            filter &&
                this.env.searchModel.query.some(
                    (query) => query.searchItemId === filter.id
                )
        );
    }

    formatAmount(amount) {
        return formatMonetary(amount, {currencyId: this.state.currency_id});
    }

    /**
     * Show only the items of the counter, keeping the grouping. A second click
     * goes back to all open items.
     *
     * @param {Object} counter
     */
    onCounterClick(counter) {
        const searchModel = this.env.searchModel;
        const filter = this.getFilter(this.isActive(counter) ? "open" : counter.filter);
        if (!filter) {
            return;
        }
        searchModel.query = searchModel.query.filter((query) =>
            GROUP_BY_TYPES.includes(searchModel.searchItems[query.searchItemId].type)
        );
        searchModel.toggleSearchItem(filter.id);
    }
}
