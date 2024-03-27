For setting the SEPA creditor identifier:

1.  Go to Invoicing/Accounting \> Configuration \> Settings.
2.  On the field "SEPA Creditor Identifier" in the section *SEPA/PAIN*,
    you can fill the corresponding identifier.

If your country requires several identifiers (like Spain), you must:

1.  Go to *Invoicing/Accounting \> Configuration \> Settings*.
2.  On the section *SEPA/PAIN*, check the mark "Multiple identifiers".
3.  Now go to *Invoicing/Accounting \> Configuration \> Management \>
    Payment Modes*.
4.  Create a payment mode for your specific bank.
5.  Fill the specific identifier on the field "SEPA Creditor
    Identifier".

For defining a payment mode that uses SEPA direct debit:

1.  Go to *Invoicing/Accounting \> Configuration \> Management \>
    Payment Modes*.
2.  Create a record.
3.  Select the Payment Method *SEPA Direct Debit for customers* (which
    is automatically created upon module installation).
4.  Check that this payment method uses the proper version of PAIN.
5.  If not, go *Invoicing/Accounting \> Configuration \> Management \>
    Payment Methods*.
6.  Locate the "SEPA Direct Debit for customers" record and open it.
7.  Change the "PAIN version" according your needs.
8.  If you need to handle several PAIN versions, just duplicate the
    payment method adjusting this field on each for having them.
