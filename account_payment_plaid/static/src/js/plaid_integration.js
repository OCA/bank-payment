/* global Plaid */
odoo.define("account_payment_plaid.plaid_integration", function (require) {
    "use strict";
    var core = require("web.core");
    var rpc = require("web.rpc");

    async function plaidLogin(env, action) {
        const handler = Plaid.create({
            onSuccess: (public_token) => {
                rpc.query({
                    model: action.params.call_model,
                    method: action.params.call_method,
                    args: [public_token, action.params.object_id],
                });
            },
            token: action.params.token,
        });
        handler.open();
    }

    core.action_registry.add("plaid_login", plaidLogin);
});
