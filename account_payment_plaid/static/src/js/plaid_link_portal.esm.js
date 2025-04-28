/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {jsonrpc} from "@web/core/network/rpc_service";

const observer = new MutationObserver(() => {
    const btn = document.getElementById("plaid-connect-btn");
    if (!btn) return;

    observer.disconnect();

    btn.addEventListener("click", async () => {
        const partnerId = parseInt(btn.dataset.partnerId, 10);
        btn.disabled = true;

        try {
            const response = await jsonrpc("/payment/plaid/get_vendor_link_token", {
                partner_id: partnerId,
            });

            const handler = window.Plaid.create({
                token: response.link_token,
                onSuccess: async (public_token, metadata) => {
                    const accounts = metadata.accounts || [];
                    const plaidButton = document.getElementById("plaid-connect-btn");

                    const container = document.getElementById(
                        "plaid-accounts-container"
                    );
                    container.innerHTML = "";

                    plaidButton.classList.add("d-none");

                    if (accounts.length === 0) {
                        container.innerHTML = `<div class="alert alert-warning">${_t(
                            "No accounts were returned."
                        )}</div>`;
                        return;
                    }

                    container.innerHTML = `
                    <div class="card shadow-sm p-4">
                        <h3 class="mb-3 text-center text-primary">${_t(
                            "Select the bank accounts to save"
                        )}</h3>
                        <form id="plaid-accounts-form">
                            <div class="row">
                                ${accounts
                                    .map(
                                        (acc) => `
                                    <div class="col-md-6 mb-3">
                                        <div class="card border-info">
                                            <div class="card-body">
                                                <div class="form-check">
                                                    <input class="form-check-input plaid-account-check" type="checkbox" value="${acc.id}" id="acc_${acc.id}">
                                                    <label class="form-check-label" for="acc_${acc.id}">
                                                        <strong>${acc.name}</strong><br/>
                                                        ****${acc.mask} <em>(${acc.subtype})</em>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>`
                                    )
                                    .join("")}
                            </div>
                            <div class="text-center">
                                <button type="submit" class="btn btn-success mt-4" id="save-plaid-accounts">
                                    ${_t("Save Selected Accounts")}
                                </button>
                            </div>
                        </form>
                    </div>
                `;

                    document
                        .getElementById("plaid-accounts-form")
                        .addEventListener("submit", async (ev) => {
                            ev.preventDefault();
                            const selected = [
                                ...document.querySelectorAll(
                                    ".plaid-account-check:checked"
                                ),
                            ].map((cb) => cb.value);
                            if (!selected.length) {
                                alert(_t("Please select at least one account."));
                                return;
                            }

                            await jsonrpc("/my/plaid/exchange_token", {
                                partner_id: partnerId,
                                public_token,
                                account_ids: selected,
                            });

                            window.location.href = "/bank/connect/success";
                        });
                },
                onExit: () => {
                    btn.disabled = false;
                },
            });

            handler.open();
        } catch (error) {
            console.error("Plaid Error:", error);
            alert("An error occurred connecting to Plaid.");
            btn.disabled = false;
        }
    });
});

observer.observe(document.body, {childList: true, subtree: true});
