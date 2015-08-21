<!doctype html>
<html>
  <meta charset="UTF-8">
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

      .important_number {
        font-weight:bold;
        font-size: 100%;
      }

      .cell {
        border:none;
      }

      .col_header {
        font-weight:bold;
        width:30px;
      }

      .col_header_third {
        font-style:italic;
      }

      .col_header_first {
        font-size: larger;
      }

      .col_date {
        width:60px;
      }

      .col_amount {
        width:100px;
      }

      .col_partner {
        /*
        Max of 2 lines in height
        */
        line-height: 15px;
        max-height: 30px;
        width:150px;
        text-overflow: ellipsis;
        overflow: hidden;
      }

      div.col_partner {
        display: -webkit-box;
        /*
        Enable ellipsis on webkit browser for 2 lines
        */
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
      }

      .right_col {
        text-align:right;
        width:100px;
      }

      .line_sum {
        border-style:solid;
        border-width:0px;
        border-bottom-width:5px;
        font-weight:bold;
        font-size: 110%;
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
          <td class="cell first_item important_number_table"
             colspan="6">
            ${_("Detailed %s account:") % rec.name} ${rec.account_id.code} -
            ${rec.account_id.name}
          </td>
        </tr>
    </table>
    <table style="width:100%;font-size:70%;">
      <thead>
          <tr>
            <td class="col_header">
            </td>
            <td class="col_header">
            </td>
            <td class="col_header">
            </td>
            <td class="line_sum col_date">
              ${_("Date")}
            </td>
            <td class="line_sum">
              ${_("Reference")}
            </td>
            <td class="line_sum col_partner">
              ${_("Partner")}
            </td>
            <td class="col_amount line_sum">
              ${_("Amount")}
            </td>
          </tr>
      </thead>
      <tr>
        <td class="left_col cell col_header col_header_first" colspan="4">
          ${_("Beginning Balance")}
        </td>
        <td>
        </td>
        <td>
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.multi_currency and rec.starting_balance_in_currency or rec.starting_balance,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Cleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines)}${_("items")}
        </td>
        <td class="cell important_number right_col">
          ${formatLang(rec.multi_currency and rec.sum_of_debits_in_currency or rec.sum_of_debits,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell">
        </td>
        <td class="cell">
        </td>
        <td class="cell">
        </td>
        <td class="col_date">
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          <div class="col_partner">
            ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
          </div>
        </td>
        <td class="cell right_col col_amount">
          ${formatLang(rec.multi_currency and rec_line.amount_in_currency or rec_line.amount,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec_line.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Cheques and Debits")}${" - %s " % int(rec.sum_of_credits_lines)}${_("items")}
        </td>
        <td class="cell important_number right_col">
          ${formatLang(rec.multi_currency and rec.sum_of_credits_in_currency or rec.sum_of_credits,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          <div class="col_partner">
            ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
          </div>
        </td>
        <td class="cell right_col">
          ${formatLang(rec.multi_currency and rec_line.amount_in_currency or rec_line.amount,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec_line.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Total Cleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col line_sum">
          ${formatLang(rec.multi_currency and rec.cleared_balance_in_currency or rec.cleared_balance,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell col_header col_header_first" colspan="4">
          ${_("Cleared Balance")}
        </td>
        <td>
        </td>
        <td>
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.multi_currency and (rec.cleared_balance_in_currency + rec.starting_balance_in_currency) or (rec.cleared_balance + rec.starting_balance),
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Uncleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col">
        </td>
      </tr>
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Deposits and Credits")}${" - %s " % int(rec.sum_of_debits_lines_unclear)}${_("items")}
        </td>
        <td class="cell important_number right_col">
          ${formatLang(rec.multi_currency and rec.sum_of_debits_unclear_in_currency or rec.sum_of_debits_unclear,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.debit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          <div class="col_partner">
            ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
          </div>
        </td>
        <td class="cell right_col">
          ${formatLang(rec.multi_currency and rec_line.amount_in_currency or rec_line.amount,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec_line.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td>
        </td>
        <td class="cell col_header col_header_third" colspan="4">
          ${_("Cheques and Debits")}${" - %s " % int(rec.sum_of_credits_lines_unclear)}${_("items")}
        </td>
        <td class="cell right_col important_number">
          ${formatLang(rec.multi_currency and rec.sum_of_credits_unclear_in_currency or rec.sum_of_credits_unclear,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %for rec_line in [line for line in rec.credit_move_line_ids if not line.cleared_bank_account]:
      <tr>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td class="cell left_col">
        </td>
        <td>
          ${rec_line.date}
        </td>
        <td>
          ${rec_line.ref and rec_line.ref or ""}
        </td>
        <td>
          <div class="col_partner">
            ${rec_line.partner_id.name and rec_line.partner_id.name or ""}
          </div>
        </td>
        <td class="cell right_col">
          ${formatLang(rec.multi_currency and rec_line.amount_in_currency or rec_line.amount,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec_line.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      %endfor
      <tr>
        <td>
        </td>
        <td class="cell col_header" colspan="4">
          ${_("Total Uncleared Transactions")}
        </td>
        <td>
        </td>
        <td class="cell right_col line_sum">
          ${formatLang(rec.multi_currency and rec.uncleared_balance_in_currency or rec.uncleared_balance,
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
      <tr>
        <td class="cell col_header col_header_first" colspan="5">
          ${_("Register Balance as of")}${" %s" % formatLang(rec.ending_date, date=True)}
        </td>
        <td>
        </td>
        <td class="cell important_number_table right_col">
          ${formatLang(rec.multi_currency and (rec.starting_balance_in_currency + rec.cleared_balance_in_currency + rec.uncleared_balance_in_currency) or (rec.starting_balance + rec.cleared_balance + rec.uncleared_balance),
                       monetary=True,
                       currency_obj=rec.multi_currency and rec.account_id.currency_id or rec.company_id.currency_id)}
        </td>
      </tr>
    </table>

    %endfor
  </body>
</html>
