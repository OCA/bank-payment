Using the Plaid API for bank transfers on production or development
environment:

1.  Go to "Settings" \> "Plaid".
2.  Add your Plaid credentials.
3.  Synchronize with Plaid.
4.  Select your bank account.
5.  Go to "Contacts" and add the plaid client id for the contact.
6.  Go to your invoice and click on "Pay with Plaid" button.nYou can see
    the button if the bill is confirmed.nWhen you click on the button,
    you will see a confirmation window.
7.  When you confirm the payment and the confirmation windownis closed
    you can see the transfer in "Settings" \> "Technical" \> "Plaid" \>
    "Transfer".
8.  When the transfer is done, you can see the bill as paid and the
    payment create on odoo.

If you are using the sandbox environment for testing, do you need to use
the simulation method for simulate the transfer. This method only works
with the sandbox environment. You can found this method on "Settings" \>
"Technical" \> "Plaid" \> "Transfer".

1.  Select the transfer that you want to simulate.
2.  Click on "Simulate Transfer" button.
3.  Select the command that you want to simulate.
    - "Simulate Transfer" : This command create a event on sandbox
      environment.nDo you need this event for check the status of the
      transfer on Odoo.
    - "Simulate transfer ledger available" : This command simulate
      converting pending balancento available balance for all
      originators in the Sandbox environment.
4.  Click on "Confirm" button.

This addon use the cron for check the status of the transfer on Plaid
and update the bill and payment. If you need more information about
Plaid, please visit the [Plaid website](https://plaid.com) or [Plaid
Docs Transfer](https://plaid.com/docs/transfer/).

In order for vendors to configure their bank accounts, we have two options:
    1 - Go to the Partner form view and click the Send Plaid Invite button.
    2 - From the Tree view, select multiple vendors and click Action → Send Plaid Invite.

Both options will send an email with instructions for the vendor to authorize and select the bank account they wish to use to receive payments through Plaid.

