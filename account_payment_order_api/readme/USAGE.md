1. Create an outbound payment order with a payment mode that has a Bank API
   Provider and add the bills as usual.
2. Confirm it. One draft payment is created per line; nothing is posted yet.
3. Click **Send to Bank**. The **Bank** tab shows the batches and the status of
   every line. If the bank requires the payments to be released (approved) on
   its own channel, do it there.
4. A scheduled action checks the batches every 10 minutes; **Check Bank Now**
   checks them at once. Paid lines are posted and reconciled, refused ones are
   freed, and the order is done when every line has a final status.
5. Lines the bank has not executed yet can be cancelled from the **Bank** tab.

With **Require Second Factor** on the payment mode, **Send to Bank** asks for a
code from the authenticator app of the user, who enables two-factor
authentication in the user profile. Each code works once and is recorded on the
order, and wrong codes lock the user out for a while. A company can also require,
in the Invoicing settings, that the user who enters the code is not the one who
confirmed the order. A payment mode without the option sends without the code.
