Payment orders that take the early payment discount of the supplier, and
preferred suppliers paid on their early payment date.

- A bill proposed in a payment order within its early payment term gets its
  discount applied (an internal credit note reconciled with it), so the
  payment is proposed for the net amount.
- A **preferred supplier** is preferred for payment: it is paid on its early
  payment date, never on its credit term. Confirming a payment order pulls in
  the bills of preferred suppliers with the same payment mode whose early
  payment falls on the day the order pays, and only those. An early payment
  date on a weekend or a holiday is paid the business day before.
- Their lines cannot be taken out of the order unless the user belongs to the
  group *Remove Preferred Suppliers from Payment Orders*.
