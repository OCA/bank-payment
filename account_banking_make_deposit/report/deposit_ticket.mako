<html>
    <head>
        <style type="text/css">
            .tablehead
            {
                border:1px solid #C0C0C0;
                font-weight: bold;
            }

            td
            {
                border: 1px solid #C0C0C0;
            }

            th
            {
                font-weight:bold;
                text-align: left;
            }

            #noborder td
            {
                border: none;
            }

            #amount
            {
                text-align: right;
            }

            #company
            {
                text-align: center;
            }

            h3
            {
                font-size: 19px;
                font-weight: 200;
            }

            ${css}
        </style>
    </head>
    <body>
        <%page expression_filter="entity" />
        <%
        def carriage_returns(text):
            return text.replace('\n', '<br />')
        %>

        %for deposit_ticket in objects:
        <% setLang(user.lang) %>

        <h1 style="clear:both;">${deposit_ticket.name or ''}</h1>

        <table class="basic_table" width="100%" cellspacing="0">
            <tr class="tablehead">
                <td>${_("Deposit From Account")}</td>
                <td>${_("Deposit To Account")}</td>
                <td>${_("Deposit Date")}</td>
                <td>${_("Journal")}</td>
                <td>${_("Force Period")}</td>
                <td>${_("Company")}</td>
            </tr>
            <tr>
                <td>${deposit_ticket.deposit_from_account_id.name}</td>
                <td>${deposit_ticket.deposit_to_account_id.name}</td>
                <td>${formatLang(deposit_ticket.date, date=True)}</td>
                <td>${deposit_ticket.journal_id and deposit_ticket.journal_id.name}</td>
                <td>${deposit_ticket.period_id.name}</td>
                <td>${deposit_ticket.company_id and deposit_ticket.company_id.name or ''}</td>
            </tr>
        </table>

        <br />

        <table class="basic_table" width="100%" cellspacing="0">
            <tr class="tablehead">
                <td>${_("Deposit Method")}</td>
                <td>${_("Deposit Bag No")}</td>
                <td>${_("Deposit Tracking No")}</td>
                <td>${_("Total Items")}</td>
                <td>${_("Amount")}</td>
                <td>${_("Memo")}</td>
            </tr>
            <tr>
                <td>${deposit_ticket.deposit_method_id and deposit_ticket.deposit_method_id.name or ''}</td>
                <td>${deposit_ticket.deposit_bag_no or ''}</td>
                <td>${deposit_ticket.bank_tracking_no or ''}</td>
                <td class="amount">${formatLang(deposit_ticket.count_total)}</td>
                <td class="amount">${formatLang(deposit_ticket.amount)}</td>
                <td>${deposit_ticket.memo or ''}</td>
            </tr>
        </table>

        <br />

        <table class="basic_table" width="100%" cellspacing="0">
            <tr class="tablehead">
                <td>${_("Prepared By")}</td>
                <td>${_("Verified By")}</td>
                <td>${_("Verified Date")}</td>
                <td>${_("State")}</td>
            </tr>
            <tr>
                <td>${deposit_ticket.prepared_by_user_id and deposit_ticket.prepared_by_user_id.name or ''}</td>
                <td>${deposit_ticket.verified_by_user_id and deposit_ticket.verified_by_user_id.name or ''}</td>
                <td>${formatLang(deposit_ticket.verified_date or '',date=True)}</td>
                <td>${deposit_ticket.get_state()}</td>
            </tr>
        </table>

        <br />

        <h3>${_("Deposit Ticket Lines")}</h3>

        <table class="list_table" width="100%" style="margin-top: 20px;" cellspacing="0" >
            <tr>
                <th>${_("Date")}</th>
                <th>${_("Name")}</th>
                <th>${_("Ref")}</th>
                <th>${_("Customer")}</th>
                <th class="amount">${_("Amount")}</th>
                <th class="company">${_("Company")}</th>
            </tr>
            %for line in deposit_ticket.ticket_line_ids:
            <tr id="noborder">
                <td> ${formatLang(line.date, date=True)}</td>
                <td> ${line.name}</td>
                <td> ${line.ref or ''}</td>
                <td> ${line.partner_id.name or ''}</td>
                <td class="amount"> ${formatLang(line.amount or '')}</td>
                <td class="company"> ${line.company_id.name or ''}</td>
            </tr>
            %endfor
        </table>
        <br />
        %endfor
    </body>
</html>
