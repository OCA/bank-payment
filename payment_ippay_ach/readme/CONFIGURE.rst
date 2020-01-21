* Activate payment acquirer named IPPay ACH
* Add API URL and API TerminalId in Ippay config. 
* Configure journal for it and allow it to make electronic payments.
* Configure the Journal's Sequence to be a simple integer (important!):

  * Implementation: Standard
  * Prefix: none
  * Suffic none
  * Use subsequences per date_range: no
  * Sequence size: 1
  * Step: 1
