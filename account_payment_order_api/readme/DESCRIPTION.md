Payment orders are usually exported as a file that someone uploads to the bank.
Many banks now take the same payments through an API, and answer for each
payment separately: some are accepted, some are refused, the accepted ones are
paid hours later, and a paid transfer can still come back.

This module adds that path to outbound payment orders:

- a payment mode gets a **Bank API Provider** (added by a provider module);
- **Send to Bank** creates one bank batch per kind of payment, reserves its
  number at the bank and records it before sending, so a timeout never leads to
  a second payment: an unknown outcome is checked at the bank, never sent again;
- each line keeps its own status (accepted, awaiting release, paid, refused,
  rejected, cancelled, returned) and the bank reason;
- the payment of a line is posted and reconciled only when the bank reports it
  as paid, with the payment date given by the bank; refused or rejected lines
  cancel their draft payment and the bill can be paid by another order right
  away; a returned payment is cancelled and the bill is open again.

This module contains no bank: provider modules implement the calls.
