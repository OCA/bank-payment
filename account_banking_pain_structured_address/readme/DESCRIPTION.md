This module adds a **Structured** option to the "PAIN.001.001.09 Address
Mode" of payment methods.

With this option, postal addresses are written with the street name, the
building number and the door number in their own elements (`StrtNm`,
`BldgNb` and `Room`), followed by `PstCd`, `TwnNm` and `Ctry`. The street
name, building number and door number come from the fields added by the
`base_address_extended` module.

`street2` has no structured element, so when it is filled it is written as
one `AdrLine` after `Ctry` (a hybrid address, which the EPC and CBPR+ rules
allow as long as the line does not repeat the structured elements).

When a partner has no street name, its address is written as in the Hybrid
mode.
