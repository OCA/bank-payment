/** @odoo-module **/

import {registry} from "@web/core/registry";

const Plaid = window.Plaid || null;

const plaidLogin = async (env, action) => {
    const {rpc} = env.services;

    const handler = Plaid.create({
        onSuccess: (public_token) => {
            rpc("/web/dataset/call_kw", {
                model: action.params.call_model,
                method: action.params.call_method,
                args: [public_token, action.params.object_id],
                kwargs: {},
            });
        },
        token: action.params.token,
    });
    handler.open();
};

registry.category("actions").add("plaid_login", plaidLogin);
