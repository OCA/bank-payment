This module adds a **Structured** option to the "PAIN.001.001.09 Address
Mode" of payment methods.

With this option, postal addresses are written with the street name and the
building number in their own elements (`StrtNm` and `BldgNb`), followed by
`PstCd`, `TwnNm` and `Ctry`, without any `AdrLine`. The street name and
building number come from the fields added by the `base_address_extended`
module.

When a partner has no street name, its address is written as in the Hybrid
mode.
