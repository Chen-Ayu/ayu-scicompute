# Capability and maturity matrix

| Domain/task | Current adapter | Maturity | Future route |
|---|---|---|---|
| Molecular SP, HOMO/LUMO, density/MEP | PySCF; ORCA | CI-validated / validated | Gaussian |
| Molecular optimization and frequency | PySCF; ORCA | CI-validated / validated | Gaussian |
| CHELPG workflow | ORCA | validated adapter workflow | Gaussian review |
| Metal complex/finite metal cluster | ORCA or reviewed PySCF | engine chain exists; chemistry validation required | Gaussian |
| Binding-energy cycle | controller + PySCF/ORCA stages | scaffolded multi-job protocol | Gaussian |
| Polymer/gel packing and classical MD | Materials Studio | scaffolded by system; engine adapter validated | open MD |
| Gel/biomass electronic descriptors | domain pack + PySCF/ORCA/MS | implemented domain workflow | method benchmark |
| Periodic molecular solid | Materials Studio where supported | scoped workflow | VASP |
| Bulk metal/magnetism | none in this release | planned | VASP |
| Surface/defect/adsorption/NEB | none in this release | planned | VASP |
| Band structure/DOS/phonons/elasticity | none in this release | planned | VASP ecosystem |

“Platform scope” is the intended architecture. “Maturity” is the present release evidence. They must never be collapsed into one marketing claim.
