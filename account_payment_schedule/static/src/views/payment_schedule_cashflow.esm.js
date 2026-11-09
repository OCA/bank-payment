/* Copyright 2026 KMEE
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
/* global Chart */

import {
    Component,
    onWillStart,
    onWillUnmount,
    useEffect,
    useRef,
    useState,
} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {KeepLast} from "@web/core/utils/concurrency";
import {_t} from "@web/core/l10n/translation";
import {deserializeDate} from "@web/core/l10n/dates";
import {formatMonetary} from "@web/views/fields/formatters";
import {loadBundle} from "@web/core/assets";

const COLORS = {
    balance: "#714B67",
    short: "#dc3545",
    inflow: "rgba(40, 167, 69, 0.55)",
    outflow: "rgba(220, 53, 69, 0.45)",
    minimum: "#6c757d",
};

export class PaymentScheduleCashflow extends Component {
    static template = "account_payment_schedule.Cashflow";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.keepLast = new KeepLast();
        this.canvasRef = useRef("canvas");
        this.state = useState({data: null, journalId: false});
        this.chart = null;
        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.load();
        });
        useBus(this.env.paymentScheduleBus, "reload", () => this.load());
        useEffect(
            () => this.renderChart(),
            () => [this.state.data]
        );
        onWillUnmount(() => this.chart && this.chart.destroy());
    }

    async load() {
        this.state.data = await this.keepLast.add(
            this.orm.call(
                "account.move.line",
                "retrieve_payment_schedule_cashflow",
                [],
                {journal_id: this.state.journalId}
            )
        );
    }

    async onJournalChange(ev) {
        this.state.journalId = parseInt(ev.target.value, 10) || false;
        await this.load();
    }

    format(amount) {
        return formatMonetary(amount, {currencyId: this.state.data.currency_id});
    }

    renderChart() {
        const data = this.state.data;
        if (!data || !this.canvasRef.el) {
            return;
        }
        if (this.chart) {
            this.chart.destroy();
        }
        const days = data.days;
        const balances = days.map((day) => day.balance);
        const pointColors = balances.map((value) =>
            value < data.minimum ? COLORS.short : COLORS.balance
        );
        const labels = days.map((day) =>
            deserializeDate(day.date).toLocaleString({day: "2-digit", month: "2-digit"})
        );
        this.chart = new Chart(this.canvasRef.el, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        type: "line",
                        label: _t("Projected Balance"),
                        data: balances,
                        borderColor: COLORS.balance,
                        pointBackgroundColor: pointColors,
                        pointBorderColor: pointColors,
                        fill: false,
                        tension: 0,
                    },
                    {
                        type: "line",
                        label: _t("Minimum Balance"),
                        data: days.map(() => data.minimum),
                        borderColor: COLORS.minimum,
                        borderDash: [4, 4],
                        pointRadius: 0,
                        fill: false,
                    },
                    {
                        label: _t("Receipts"),
                        data: days.map((day) => day.inflow),
                        backgroundColor: COLORS.inflow,
                    },
                    {
                        label: _t("Payments"),
                        data: days.map((day) => -day.outflow),
                        backgroundColor: COLORS.outflow,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                animation: false,
                interaction: {mode: "index", intersect: false},
                scales: {
                    y: {ticks: {callback: (value) => this.format(value)}},
                },
                plugins: {
                    legend: {position: "bottom"},
                    tooltip: {
                        callbacks: {
                            label: (item) =>
                                `${item.dataset.label}: ${this.format(item.parsed.y)}`,
                            footer: (items) => {
                                const day = days[items[0].dataIndex];
                                return [
                                    `${_t("Scheduled")}: ${this.format(day.queue)}`,
                                    `${_t("In Draft Order")}: ${this.format(day.draft)}`,
                                    `${_t("At the Bank")}: ${this.format(day.bank)}`,
                                ];
                            },
                        },
                    },
                },
            },
        });
    }
}
