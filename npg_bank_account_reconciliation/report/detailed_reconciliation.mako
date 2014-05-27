<html>
  <head>
    <style type="text/css">
      table {
      page-break-inside:auto
      }
      table tr {
      page-break-inside:avoid;
      page-break-after:auto;
      }
      thead {
      display:table-header-group;
      }
      .important_number_table {
      font-weight:bold;
      font-size: 110%;
      }
      .cell {
      border:none;
      }
      .left_col {
      width:40%;
      }
      .col_header {
      }
      .right_col_sum {
      width:20%;
      text-align:right;
      }
      .right_col {
      text-align:right;
      }
      .second_line {
      padding-left:3em;
      }
      .third_line {
      padding-left:6em;
      }
      .line_sum {
      border-style:solid;
      border-width:0px;
      border-bottom-width:5px;
      }
      .first_item {
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
    <table style="width:100%;">
        <tr>
          <td class="cell left_col first_item important_number_table"
              colspan="6">
            ${_("Detailed %s account:") % rec.name} ${rec.account_id.code} -
            ${rec.account_id.name}
          </td>
        </tr>
    </table>
    <table style="width:100%;font-size:70%;">
      <thead>
          <tr>
            <td>
            </td>
            <td class="line_sum">
              ${_("Date")}
            </td>
            <td class="line_sum">
              ${_("Name")}
            </td>
            <td class="line_sum">
              ${_("Reference")}
            </td>
            <td class="line_sum">
              ${_("Partner")}
            </td>
            <td class="line_sum">
              ${_("Amount")}
            </td>
          </tr>
      </thead>
      <tr>
        <td class="left_col cell">
          ${_("Beginning Balance")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col">
          ${formatLang(rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell second_line left_col">
          ${_("Cleared Transactions")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Cheques and Payments")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col">
          ${formatLang(rec.sum_of_debits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell third_line left_col">
        </td>
        <td class="col_header">
          ${rec_line.date}
        </td>
        <td class="col_header">
          ${rec_line.name}
        </td>
        <td class="col_header">
          ${rec_line.ref}
        </td>
        <td class="col_header">
          ${rec_line.partner_id.name}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td class="cell third_line left_col">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_credits_lines)}${_("items")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell line_sum right_col">
          ${formatLang(-rec.sum_of_credits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell third_line left_col">
        </td>
        <td class="col_header">
          ${rec_line.date}
        </td>
        <td class="col_header">
          ${rec_line.name}
        </td>
        <td class="col_header">
          ${rec_line.ref}
        </td>
        <td class="col_header">
          ${rec_line.partner_id.name}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td class="cell second_line left_col">
          ${_("Total Cleared Transactions")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col line_sum">
          ${formatLang(rec.cleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell left_col">
          ${_("Cleared Balance")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.cleared_balance + rec.starting_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell second_line left_col">
          ${_("Uncleared Transactions")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Cheques and Payments")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col">
          ${formatLang(rec.sum_of_debits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell third_line left_col">
        </td>
        <td class="col_header">
          ${rec_line.date}
        </td>
        <td class="col_header">
          ${rec_line.name}
        </td>
        <td class="col_header">
          ${rec_line.ref}
        </td>
        <td class="col_header">
          ${rec_line.partner_id.name}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td class="cell third_line left_col">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_credits_lines_unclear)}${_("items")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col line_sum">
          ${formatLang(-rec.sum_of_credits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell third_line left_col">
        </td>
        <td class="col_header">
          ${rec_line.date}
        </td>
        <td class="col_header">
          ${rec_line.name}
        </td>
        <td class="col_header">
          ${rec_line.ref}
        </td>
        <td class="col_header">
          ${rec_line.partner_id.name}
        </td>
        <td class="cell right_col">
          ${formatLang(rec_line.amount, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td class="cell second_line left_col">
          ${_("Total Uncleared Transactions")}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell right_col line_sum">
          ${formatLang(rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell left_col">
          ${_("Register Balance as of")}${" %s" % formatLang(rec.ending_date, date=True, currency_obj=rec.company_id.currency_id)}
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="col_header">
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.starting_balance + rec.cleared_balance + rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
    </table>

    <table style="width:100%">
      <tr>
        <td class="cell left_col first_item important_number_table"
            colspan="2">
          ${_("Summary %s account:") % rec.name} ${rec.account_id.code} -
          ${rec.account_id.name}
        </td>
      </tr>
      <tr>
        <td class="left_col cell">
          ${_("Beginning Balance")}
        </td>
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
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Cheques and Payments")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
        </td>
        <td class="cell right_col_sum">
          ${formatLang(rec.sum_of_debits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_credits_lines)}${_("items")}
        </td>
        <td class="cell line_sum right_col_sum">
          ${formatLang(-rec.sum_of_credits, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell second_line left_col">
          ${_("Total Cleared Transactions")}
        </td>
        <td class="cell right_col_sum line_sum">
          ${formatLang(rec.cleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell left_col">
          ${_("Cleared Balance")}
        </td>
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
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Cheques and Payments")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
        </td>
        <td class="cell right_col_sum">
          ${formatLang(rec.sum_of_debits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell third_line left_col">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_credits_lines_unclear)}${_("items")}
        </td>
        <td class="cell right_col_sum line_sum">
          ${formatLang(-rec.sum_of_credits_unclear, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell second_line left_col">
          ${_("Total Uncleared Transactions")}
        </td>
        <td class="cell right_col_sum line_sum">
          ${formatLang(rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell left_col">
          ${_("Register Balance as of")}${" %s" % formatLang(rec.ending_date, date=True, currency_obj=rec.company_id.currency_id)}
        </td>
        <td class="cell important_number_table right_col_sum">
          ${formatLang(rec.starting_balance + rec.cleared_balance + rec.uncleared_balance, monetary=True, currency_obj=rec.company_id.currency_id)}
        </td>
      </tr>
    </table>

    %endfor
  </body>
</html>
