# Software router

| Scientific need | Default route | Alternative | Boundary |
|---|---|---|---|
| Finite molecule/cluster SP, HOMO/LUMO, density or MEP cube | PySCF | ORCA | Prefer PySCF for a fully open stack |
| Finite molecule geometry optimization or frequency | PySCF | ORCA | Require optional optimizer dependency for PySCF optimization |
| CHELPG charges or an established ORCA protocol | ORCA | PySCF MEP cube | ORCA is user-supplied external software |
| Polymer packing, amorphous cell, XSD/XTD workflow | Materials Studio | preparation-only | Requires a user-licensed installation |
| Classical polymer/gel MD and MS-native analysis | Materials Studio | another future open MD adapter | Do not route to molecular DFT |
| No executable/process tools | preparation-only | none | Generate inputs; never claim execution |

Do not compare total energies across engines or inconsistent methods as one binding-energy cycle. Use one engine per internally compared set unless a documented cross-engine validation is the scientific purpose.
