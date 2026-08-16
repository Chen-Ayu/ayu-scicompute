# Positioning, novelty and related work

AyuSciCompute does not introduce a new density functional, force field, electronic-structure solver or MD integrator. Its contribution is an evidence-gated agent control layer that turns research intent into executable, maturity-aware and auditable molecular/materials workflows.

Its differentiating combination is: bilingual scientific contracts; separated orchestration, domain packs and adapters; explicit current-versus-roadmap maturity; open and user-supplied proprietary engines without redistribution; separate process/scientific states; cross-model execution instructions; and conclusions traceable to real raw output.

## Relationship to established platforms

- [AiiDA](https://aiida.readthedocs.io/projects/aiida-core/en/stable/intro/index.html) provides mature database-backed provenance, remote execution and high throughput. AyuSciCompute is lighter and agent-facing; it does not yet match AiiDA's scale or provenance graph.
- [atomate2](https://materialsproject.github.io/atomate2/) provides composable production workflows for materials calculations. AyuSciCompute emphasizes natural-language contracts, cross-model execution and heterogeneous license boundaries.
- [ASE](https://ase-lib.org/index.html) provides the established `Atoms`/calculator abstraction and atomistic algorithms. The open MD roadmap should integrate that ecosystem where appropriate rather than recreate it.
- [QCEngine](https://molssi.github.io/QCEngine/) standardizes execution and structured results across quantum-chemistry programs. Future schemas should align with community standards where feasible.

The advanced element is the trust boundary: a roadmap item cannot become an implemented adapter by wording alone, and a normal exit cannot become a scientific result without observable-specific evidence.

## Current limitations

- no Gaussian or VASP runner in this release;
- no database/scheduler-grade provenance comparable to AiiDA;
- no broad molecular/materials benchmark or uncertainty study;
- no validated open classical-MD backend;
- no peer-reviewed accuracy or productivity comparison.
