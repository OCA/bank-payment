1. In _Invoicing \> Configuration \> Settings_, set the _Early Discount Gain_ and _Early
   Discount Loss_ accounts (used by Odoo for the native early payment discount).
2. Give vendors payment terms with _Early Discount_ (percentage, days and the tax
   computation of the discount).
3. On the payment modes used in payment orders (_Invoicing \> Configuration \> Payment
   Modes_), section _Early Payment Discount_:
   - _Pay Early Discounts on Discount Date_: bills with a discount are selected and
     scheduled by their discount date instead of their due date;
   - _Extend Discount Period to Next Working Day_: a discount period ending on a
     non-working day (weekend or public holiday of the company's working-time calendar)
     is extended to the next working day;
   - _Early Discount Buffer Days_: bills are selected and scheduled that many days
     before the end of the discount period (on the working day before), so that the
     money reaches the supplier in time, e.g. 1 to transfer one day early. Count the
     days the transfer needs to be credited to the supplier, which can be more for
     cross-border or non-SEPA payments. The discount itself stays valid until the end of
     the discount period;
   - _Early Discount Grace Days_: additional days after the end of the discount period
     during which the discount is still deducted, relying on the supplier's goodwill.
