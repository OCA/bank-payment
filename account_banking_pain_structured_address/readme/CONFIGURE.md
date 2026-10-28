1.  Open the payment method used by your PAIN.001.001.09 payment mode, for
    example *SEPA Credit Transfer to suppliers*.
2.  Set **PAIN.001.001.09 Address Mode** to *Structured (street name and
    number)*.
3.  Check that your partners have their street name and building number
    filled in. Both are set from the street when it is entered, and can be
    corrected on the partner form.

Installing `base_address_extended` also splits the street of all existing
partners automatically, with a heuristic. Review the result before switching
to Structured: some address formats are split wrongly, for example
`Hauptstraße 12/Stiege 2/Top 5` becomes the street name
`Hauptstraße 12/Stiege 2/Top` with building number `5`. The file is still
valid, but the bank gets the wrong building number. Correct such partners on
the partner form (street name, building number, door number and street2).

If the module is uninstalled, payment methods using the Structured mode are
set to Hybrid.
