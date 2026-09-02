This module doesn't add any feature, but it is used by several other
modules.

It only enforces that two active payment modes of the same company cannot
share the same name. The comparison ignores case and surrounding blanks, so
*BOLETO*, *Boleto* and *boleto* are considered to be the same name. Archived
payment modes are ignored, and the same name can still be used in another
company.

Duplicating a payment mode keeps working: the copy is named *&lt;name&gt; (copy)*
when the original name is already taken in the target company.
