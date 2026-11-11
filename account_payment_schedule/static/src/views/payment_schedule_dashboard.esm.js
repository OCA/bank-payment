/** @odoo-module */
/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {useBus, useService} from "@web/core/utils/hooks";
import {PaymentScheduleCashflow} from "@account_payment_schedule/views/payment_schedule_cashflow.esm";
import {formatMonetary} from "@web/views/fields/formatters";

const {Component, onWillStart, useState} = owl;

const GROUP_BY_TYPES = ["groupBy", "dateGroupBy"];

export class PaymentScheduleDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({counters: [], currency_id: false});
        onWillStart(() => this.load());
        // Reload after every change of the list: edits, new orders, other filters.
        useBus(this.props.model, "update", () => this.load());
    }

    async load() {
        const data = await this.orm.call(
            "account.move.line",
            "retrieve_payment_schedule_dashboard",
            [this.env.searchModel.globalDomain]
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

PaymentScheduleDashboard.template = "account_payment_schedule.Dashboard";
PaymentScheduleDashboard.props = {model: Object};
PaymentScheduleDashboard.components = {PaymentScheduleCashflow};
