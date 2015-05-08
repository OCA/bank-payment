<html>
  <head>
    <style type="text/css">
      table {
      page-break-inside:auto
      }

      table tr {
      page-break-inside:avoid; page-break-after:auto;
      }
      .important_number_table
      {
      font-weight:bold;
      font-size: 110%;
      }
      .cell
      {
      border:none;
      }
      .left_col
      {
      }
      .col_header
      {
      }
      .right_col_sum
      {
      width:20%;
      text-align:right;
      }
      .right_col
      {
      text-align:right;
      }
      .second_line
      {
      padding-left:3em;
      }
      .third_line
      {
      padding-left:6em;
      }
      .line_sum
      {
      border-style:solid;
      border-width:0px;
      border-bottom-width:5px;
      }
      .first_item
      {
      text-align:center;
      border-style:solid;
      border-width:0px;
      border-bottom-width:8px;
      }
      ${css}
    </style>
  </head>
  <body>
    %for rec in objects:
      <table style="width:100%">
        <tr>
          <% cols = 3 if rec.multi_currency else 2 %>
          <td class="cell left_col first_item important_number_table"
              colspan="${cols}">
            ${_("Summary account:")} ${rec.account_id.code} -
            ${rec.account_id.name}
          </td>
        </tr>
        <tr>
          <td class="left_col cell">
            ${_("Beginning Balance")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum">
                ${formatLang(rec.starting_balance_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif 
          <td class="cell right_col_sum">
            ${formatLang(rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Cleared Transactions")}
          </td>
          <td class="cell right_col_sum">
          </td>
          <td class="cell right_col_sum">
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum">
                ${formatLang(rec.sum_of_debits_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell right_col_sum">
            ${formatLang(rec.sum_of_debits, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Cheques and Debits")}${" - %s " % int(rec.sum_of_credits_lines)}${_("items")}
          </td>
          %if rec.multi_currency:
              <td class="cell line_sum right_col_sum">
                ${formatLang(-rec.sum_of_credits_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell line_sum right_col_sum">
            ${formatLang(-rec.sum_of_credits, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Total Cleared Transactions")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum line_sum">
                ${formatLang(rec.cleared_balance_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell right_col_sum line_sum">
            ${formatLang(rec.cleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell left_col">
            ${_("Cleared Balance")}
          </td>
          %if rec.multi_currency:
              <td class="cell important_number_table right_col_sum">
                ${formatLang(rec.cleared_balance_in_currency + rec.starting_balance_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell important_number_table right_col_sum">
            ${formatLang(rec.cleared_balance + rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Uncleared Transactions")}
          </td>
          <td class="cell right_col_sum">
          </td>
          <td class="cell right_col_sum">
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum">
                ${formatLang(rec.sum_of_debits_unclear_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell right_col_sum">
            ${formatLang(rec.sum_of_debits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell third_line left_col">
            ${_("Cheques and Debits")}${" - %s " % int(rec.sum_of_credits_lines_unclear)}${_("items")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum line_sum">
                ${formatLang(-rec.sum_of_credits_unclear_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell right_col_sum line_sum">
            ${formatLang(-rec.sum_of_credits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell second_line left_col">
            ${_("Total Uncleared Transactions")}
          </td>
          %if rec.multi_currency:
              <td class="cell right_col_sum line_sum">
                ${formatLang(rec.uncleared_balance_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell right_col_sum line_sum">
            ${formatLang(rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
        <tr>
          <td class="cell left_col">
            ${_("Register Balance as of")}${" %s" % formatLang(rec.ending_date, date=True, currency_obj=rec.company_id.currency_id)}
          </td>
          %if rec.multi_currency:
              <td class="cell important_number_table right_col_sum">
                ${formatLang(rec.starting_balance_in_currency + rec.cleared_balance_in_currency + rec.uncleared_balance_in_currency, monetary=True, currency_obj=rec.account_id.currency_id)}
              </td>
          %endif
          <td class="cell important_number_table right_col_sum">
            ${formatLang(rec.starting_balance + rec.cleared_balance + rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
          </td>
        </tr>
      </table>

    %endfor
  </body>
</html>
