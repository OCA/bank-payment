* Create a Payment Mode dedicated to SEPA Credit Transfer.

* Select the Payment Method *SEPA Credit Transfer to suppliers* (which is
  automatically created upon module installation).

* Check that this payment method uses the proper version of PAIN.

** PAIN.001.001.09 address handling **

When using format **pain.001.001.09**, the address block is no longer generated
using the legacy unstructured format, as this is invalid according to the
official schema.

You must configure the field “PAIN.001.001.09 Address Mode” on the payment
method:

- **Minimal (City + Country)**
  Generates only the mandatory structured elements `TwnNm` and `Ctry`.

- **Hybrid (City/Country + AdrLine)**
  Generates `TwnNm` and `Ctry`, plus optional `AdrLine` elements for street data.

If no address mode is selected, the default is **Minimal**, which is fully
schema-compliant.

Older PAIN formats (`pain.001.001.03`, `.04`, `.05`, etc.) are unaffected.
