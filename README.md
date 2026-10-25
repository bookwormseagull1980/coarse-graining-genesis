# Coarse-Graining Genesis Framework

## Reproducible physics from a common generating source

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22067005.svg)](https://doi.org/10.5281/zenodo.22067005)

**Jinku Guo · Northwestern Polytechnical University**

[Research portal](https://bookwormseagull1980.github.io/Book-and-Articles/) ·
[Reviewer guide](REVIEWER_START_HERE.md) · [Release facts](docs/RELEASE_FACTS.md) ·
[Complete technical reference](REFERENCE.md) · [Discussions](https://github.com/bookwormseagull1980/coarse-graining-genesis/discussions)

V5 is the executable numerical branch of a mathematical-physics programme
starting from minimal unbiased compositional change. It follows one source
record through compact spectral geometry, gauge-matter response, effective
couplings, mass scales, emergent gravity and cosmological observables.

The distinctive feature is the common input structure. Several outputs depend
on the same finite spectral response and normalization, so a source change
propagates across sectors in a reproducible way. The code retains those
dependencies, the finite response domain, interval enclosures and comparison
data. The companion [Lean library](https://github.com/bookwormseagull1980/Lean-Formalization-of-Arithmetic-and-Basic-Physical-Interfaces)
gives the formal source construction and the generated Yang-Mills operator
theorems.

![From minimal unbiased change to internal structure and shared quantitative physical response](.github/physical-derivation.png)

## Main calculations and results

| Sector | Result or construction | Where to examine it |
| --- | --- | --- |
| Spectral response | Selected level R=5 and an exact eight-branch response reduction; a unique TT endpoint near 2.49353433 | [Structural closure](docs/STRUCTURAL_CLOSURE.md), [TT equivalence](docs/TT_EQUIVALENCE.md) |
| Gauge and matter | Common-source gauge-matter bundle, scalar response and effective-coupling readouts | [Framework ledger](docs/V5_LEDGER.md) |
| Generated Yang-Mills gap | TT-endpoint generated gap, its relation to the formal IR-edge operator and the separate low-energy effective readout | [Lean correspondence](docs/LEAN_CORRESPONDENCE.md) |
| Mass relations and matching | A charged-lepton relation in the six-fermion geometric setting, finite matching and mass-scale propagation | [Papers index](docs/PAPERS.md), [technical reference](REFERENCE.md) |
| Gravity | Source-to-readout tensor response with the retained direct term and source/binding contributions | [Scientific overview](docs/papers_overview.pdf), [framework ledger](docs/V5_LEDGER.md) |
| Cosmology | Expansion and structure readouts, thermal and abundance calculations, with separately recorded observational comparisons | [Release facts](docs/RELEASE_FACTS.md), [precision budget](docs/PRECISION_BUDGET.md) |

### One input record, correlated physical outputs

The finite response-domain calculation has a selected level and a certified
endpoint enclosure. The same record enters effective couplings, matter scales
and macroscopic readouts. This gives a concrete way to test cross-sector
compatibility: change a generating quantity once, propagate its dependencies,
and examine the joint response.

The programme retains the action evaluated on the generated fields and the
difference between a complete response and a radial replacement. Finite windows
also retain memory, source moments and return from eliminated degrees of
freedom. The [full reference](REFERENCE.md) explains these mechanisms and their
numerical consequences.

### Generated Yang-Mills and radius realizations

The formal IR-edge model has a source-generated nonlinear curvature action,
a complete original-field differential Hessian, a unique self-adjoint closure
and an attained positive spectral bottom. V5 evaluates the separate
transverse-traceless endpoint realization. Its enclosure and exact finite-branch
reduction provide the numerical interface to the corresponding Lean endpoint
certificate.

The Gaussian IR edge and the TT endpoint are different radius realizations.
The generated gap and the low-energy glueball catalogue are also different
readouts. Their source definitions, dimensions and comparison roles are
specified in [the correspondence document](docs/LEAN_CORRESPONDENCE.md).

## Run a first calculation

The standard-library spectral example supplies a small, inspectable result:

```sh
python examples/quickstart/run_example.py
python scripts/certify_tt_response.py
```

The first command generates a three-shell scalar record on the projective
carrier and checks its output. The second computes the finite response-domain
endpoint certificate and the selected integer level.

For the core regression suite:

```sh
python -m pip install -r requirements-lock.txt
python -m pytest -q -m "not numerical and not auxiliary" -p no:cacheprovider
```

The lock file records the tested Python 3.13.12 environment.
[requirements.txt](requirements.txt) gives compatible lower bounds for ordinary
installation. The [reviewer guide](REVIEWER_START_HERE.md) gives the full release
reproduction, including audits and the optional cosmology calculations.
The [Actions page](https://github.com/bookwormseagull1980/coarse-graining-genesis/actions)
shows current branch regression runs.

## Reading a numerical record

The current release-facts document identifies run
`20261025T021453Z-a4c66902`: 262 parameter records, 261 derived records and
zero pending records. It records 648 passing CI-core tests from a separate
run; the full suite was not rerun for that record. These figures describe the
named record and are kept in [docs/RELEASE_FACTS.md](docs/RELEASE_FACTS.md).

A derived quantity, an interval certificate and an observational statistic
answer different questions. The source ledger states how a quantity is
constructed. A certificate encloses its specified calculation. A comparison
uses the stated observed inputs, covariance and matching scheme. The release
records keep these layers separate so that a successful check has a precise
scientific meaning.

For example, the cosmological record includes sigma_8 near 0.81233 and S_8 near
0.83226. The precision budget explains the associated input and finite-window
information. The complete technical reference retains the numerical discussion,
including comparisons that reveal tensions and their physical remainder.

## Documentation and companion work

- [Scientific graphical overview](docs/papers_overview.pdf) introduces the common
  source, geometry, response, matching and macroscopic layers.
- [Papers index](docs/PAPERS.md) links the companion manuscripts.
- [Framework ledger](docs/V5_LEDGER.md) traces the physical construction and inputs.
- [Precision budget](docs/PRECISION_BUDGET.md) describes endpoint and abundance errors.
- [Structural closure](docs/STRUCTURAL_CLOSURE.md) and
  [TT equivalence](docs/TT_EQUIVALENCE.md) specify the certificate interfaces.
- [Lean correspondence](docs/LEAN_CORRESPONDENCE.md) maps numerical and formal results.
- [Complete technical reference](REFERENCE.md) preserves the full research
  introduction, mechanisms and detailed results.

The [shared research portal](https://bookwormseagull1980.github.io/Book-and-Articles/)
connects these calculations with generated arithmetic, prime operators,
long-range response and certified computation. All reading copies and their
individual DOIs are in
[Book-and-Articles](https://github.com/bookwormseagull1980/Book-and-Articles).

## Citation and scientific feedback

Cite V5 using its concept DOI,
[10.5281/zenodo.22067005](https://doi.org/10.5281/zenodo.22067005),
and the companion paper for the result being used.
[CITATION.cff](CITATION.cff) contains the software metadata.
[LICENSE](LICENSE) states the copyright and attribution requirements.

Use [Discussions](https://github.com/bookwormseagull1980/coarse-graining-genesis/discussions)
for mathematical or physical questions. A reproducibility issue should identify
the command, source revision, environment and affected record; the issue form
provides space for these details.

Subjects: computational physics, generated gauge structure, Yang-Mills mass
gap, Standard Model, spectral geometry, effective couplings, electroweak
matching, emergent gravity, cosmology, validated numerics and interval arithmetic.
