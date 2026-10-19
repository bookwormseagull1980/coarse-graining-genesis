<!--
Coarse-Graining Genesis Framework V5.0
Author: Jinku Guo <guojk@nwpu.edu.cn>
Northwestern Polytechnical University, Xi'an 710072, China
ORCID: 0009-0000-6600-6171
References:
DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
Full bibliography: REFERENCES.md and CITATION.cff.
-->

# Reviewer start here

This guide describes the reproduction and verification of Coarse-Graining
Genesis Framework V5, version 5.0.1. The software citation is in
`CITATION.cff`; the V5 version-series DOI is
[10.5281/zenodo.22067005](https://doi.org/10.5281/zenodo.22067005), and
[REFERENCES.md](REFERENCES.md) provides the full author–year
bibliography for the cited manuscripts.

## Inputs and scientific definitions

The observed dimensional anchor is `G_N_PDG`, which fixes the Planck scale.
The compact spectrum, finite matter content, `R=5` response domain,
normalizations and matching conditions are the structural inputs stated
in the papers. The store labels the dimensional anchor, derived records and
the `SCALE_CHOICE` bookkeeping record separately.

Observed reference values and cosmological data are kept in
`comparison/reference_inputs.json`. Derived comparison results are registered in
`cg_params.json` with the comparison role. CAMB propagates the fixed generated
input set; DESI and other observations enter the subsequent comparison.
All modules use the common parameter interface for these two stores.
The run manifest records their identities and verification status.
Comparison propagation settings are registered separately from generated
physical parameters; numerical accuracy controls remain explicit at execution.

Quantity definitions identify the carrier, operator, source, projection,
normalization, units, scale, scheme and approximation. Explicit direct-input
sets record the stored values used in each output. The physical matching
formulas and their conditions are described in the
[framework ledger](docs/V5_LEDGER.md).

## Files to inspect

| File | Role |
|---|---|
| `cg_params.json` | Unified scalar and structured scientific results, definitions and dependencies |
| `run_manifest.json` | Run identity, source/output fingerprints and structured verification state |
| `V5_VERIFICATION_REPORT.md` | Executed checks and their scope |
| `docs/V5_LEDGER.md` | Spectral, matter, numerical, gravity and cosmology methods |
| `comparison/reference_inputs.json` | Observational reference values, BAO vector/covariance and their data identities |
| `docs/reviewer_dashboard.html` | Calculation dependencies and comparison overview |

The ledger specifies each response domain and normalization, transfer
conventions and the interpretation of numerical and interval errors.
The unified records include finite-operator examples, matter matching,
complete condensates, tensor and local responses, thermal evolution and
CAMB/BAO calculations. Conditional examples retain their supplied parameters.

The zero-argument `generated_matter_bundle()` constructs the concrete source
bundle independently of the general localized-bundle comparison interfaces.
`tests/test_canonical_matter_bundle.py` checks its actual source operators,
neutral coordinate, determinant signature and frame compatibility. The same
suite checks the exact rational affine-dilation variation that detects the
relative cubic self-coupling. General configuration identities and the unique
coefficient in the normalized first-order class are proved by the Lean
`CanonicalMatterBundle` and `SourceNonlinearTensorAction` modules; full local
nonlinear metric equations are not included in that formalization.

## Reproduce and verify

From the repository root, install the runtime and verification dependencies:

```powershell
py -m pip install -r requirements.txt
py -m pip install "pytest>=7.4" "mpmath>=1.3"
```

Then execute:

```powershell
py scripts/verify_v5.py --fresh --audit --pytest
```

This executes the calculation from empty temporary stores, validates source
and output fingerprints, checks input provenance and observational-data
isolation, and runs the Python test suite. A completed report identifies each
executed check and any optional check that was not run.
The five complete source and store audits execute once. Provenance and
observation-isolation results from this invocation's reproduction are reused
after the published run and file identities are verified; the remaining
audits execute in the verifier. Their test wrappers are deselected during
the combined invocation. An independent `pytest` run includes those wrappers.
Test calculations use temporary directories outside the distributed source tree.

To verify the same calculated run without repeating the production chain:

```powershell
py scripts/verify_v5.py --no-reproduce --pytest
```

For the core checks of the same recorded run:

```powershell
py scripts/verify_v5.py --no-reproduce --pytest --test-scope core
```

The core suite checks algebraic identities, interfaces and data isolation.
The `numerical` group adds independent quadrature, rational interval bounds,
cutoff and discretization refinement, and complete response examples. The
`auxiliary` group checks presentation of recorded verification. A core report
explicitly lists the omitted groups. A release verification uses the full
suite (`--test-scope all`, the default with `--pytest`). Runtime installation
does not require the verification dependencies or execute the tests.

During implementation, run the affected module without rebuilding unrelated
sectors, for example:

```powershell
py -m pytest tests/test_matter_source_response.py -q
```

Changing source files invalidates the corresponding recorded identities;
the `--no-reproduce` command requires an unchanged, identified calculation.

The manifest check requires the calculation sources, verification sources and
saved outputs to agree with the recorded fingerprints. Completed CAMB
propagation is reused after its inputs and configuration pass validation.
BAO and SPARC statistics are evaluated from the registered observations and
the applicable propagation or local-response inputs.

For an independent empty-store determinism check:

```powershell
py scripts/verify_v5.py --fresh --audit --pytest --stability
```

This optional command performs an additional full-chain calculation with
fresh response evaluations. The comparison uses all scientific records from the two executions,
including structured response evaluations. Run identities distinguish
executions and are excluded from that equality test.

## Spectral and finite-algebra checks

The endpoint certificate evaluates outward rational bounds and prints its
result:

```powershell
py scripts/certify_spectral_inputs.py
```

Its interval certifies the three retained positions on the specified response
domain. The explicit finite-domain endpoint certificate evaluates `c(R)` for
`R=4,5,6`, the lower platform edge `R_*`, and the shell-support upper bound:

```powershell
py scripts/certify_tt_response.py
```

It prints the positive endpoint coordinates `c(4), c(5), c(6)`, the lower edge
`R_*`, and the unique integer level in `(R_*, 16/pi]`. The production
realization gives `c(4) < sqrt(11/2)` and `c(6) < sqrt(15/2)`; the upper edge
is therefore the shell-support bound `R <= 16/pi`, not a crossing of `c` at
`sqrt(15/2)`. These are floating-point centre values; an outward interval
certificate is a separate calculation. High-precision floating-point central
values and observational residuals have their own accuracy statements. A
supplied native-condensate problem can be certified separately:

```powershell
py scripts/solve_native_condensate.py --g 1 --Z 2 --L 2.5 --shells 512
```

Both certificate commands print their results to standard output. Their
mathematical bounds, response units and interpretation are given in the
ledger. They provide explicit parameter examples; the production run
registers its scientific results through the common parameter interface.

Lean 4.7 compiles the finite integer and rational formalizations. It can be
located through `PATH`, `LEAN_EXE` or the standalone verifier's
`--lean-exe` option. To include complete archive compilation:

```powershell
py scripts/verify_v5.py --fresh --audit --lean --pytest
```

The selected suite is available through `--lean-key-only`; it covers matter
counts, two-loop coefficients and the rest-frame cold-source decomposition.
The report records the exact compilation scope. The separate Lean source audit
checks the archive's declared formalization discipline.

The shared foundations of the arithmetic and gauge-structure papers are
maintained in the independent library *Lean Formalization of Arithmetic and
Basic Physical Interfaces*. Its Lean version and mathlib commit are locked
within that project. They are independent of the Lean 4.7 archive above.
V5 keeps only `foundations-reference.json`, which pins the complete proof
source inventory, dependency locks and external verification program.

Place its checkout in a sibling directory named `Foundations-from-Minimal-Change`,
or select another location through `FOUNDATIONS_PROJECT`. To add a newly
compiled proof audit to a V5 verification, use:

```powershell
py scripts/verify_v5.py --no-reproduce --foundations --foundations-project <proof-checkout>
```

`--foundations-lake-exe <lake-executable>` selects the independent project's
Lake executable when needed. For a proof check without running V5's numerical
checks or updating its run manifest, use the thin adapter directly:

```powershell
py scripts/verify_foundations.py --project <proof-checkout>
```

The adapter rejects a checkout whose proof sources or verifier differ from
the pinned reference. The aggregate V5 check requires a new successful audit
identity and validates the resulting record and log. Stored evidence contains
portable identities, not the local checkout path. To check that evidence later
from a non-default checkout, set `FOUNDATIONS_PROJECT` to its location again.
The numerical calculation remains available when the independent proof library
is absent. The local `lean_proofs/` archive remains part of V5.

## Macroscopic gravity and matter interfaces

The stored tensor coefficients include the internal critical coordinate,
external momentum-conversion slope, kinetic normalization, physical helicity
residue and static conserved-source coefficient. Their definitions are in
`cg_params.json`; its structured response records evaluate the physical
polarizations, gauge identity, reflection form and momentum matching.
The classical completion uses the common Einstein--scalar action and the
Noether identities proved in Guo (2026f).
The independent foliation field in Guo (2026g) gives the same RMS flux
in its stationary weak-field limit and embeds the Einstein--matter
solutions with a smooth geodesic foliation. On the dust and constant-vacuum
background, constraint reduction gives positive kinetic coefficients
`1/D` and `C` for the total cold-source mode and the relative clock.
The corresponding finite evolutions check exact Einstein--de Sitter
solutions, conservation of the foliation momentum, and equivalent
partitions of one total cold source. The action follows the formalism
of Blanchet and Marsat (2011); see also Blanchet and Skordis (2024).

The matter calculation includes finite connectors, complete mode products,
spatial kinetic Grams, vertices, family normalization and finite
renormalization in the schemes stated with each example. The generated
static neutrino masses supply the thermal calculation. The environmental
oscillation readout is recorded separately.

The cosmological record resolves the endpoint budget into cold matter,
photons and thermal neutrinos. The cold-source examples evolve their specified
initial data until characteristic crossing, and the local static response
uses explicit source and boundary data. Conditional coupled flows and nuclear
rate examples retain their supplied effective-action or reaction-rate inputs.

The local nonlinear field also drives finite plane material cells through
the common variational force and consistent mass matrix. The registered
example compares two time steps, while independent tests check force-energy
variation, time-dependent boundary work, and termination at cell crossing.

Joint diagnostics include the geometric six-mass relation, full covariance
propagation for independently supplied physical matching coefficients,
and the common electron/electroweak response to bandwidth. The charged-lepton
combination `m_mu^2/(m_e*m_tau)=exp(sqrt(2*pi))` supplies an additional
constraint independent of the endpoint and bandwidth. The common-scale
seven-mass covariance of Huang and Zhou (2021) gives the required weighted
finite-matching combinations `Delta_F=2.69537 +/- 1.48017` and
`Delta_L=0.0112736 +/- 0.0005817`. Their shared covariance is retained;
the individual finite matching factors are supplied by the relevant
source-vertex calculation.

A monotone
interval enclosure with positive infinite tails certifies the three-position
platform for every R>=5. At fixed active shell support, the joint generation
condition is `R_* < R <= 16/pi`, with `R_* ~= 4.0187119842`.
A separate 480-cell rational enclosure certifies the crossing's position
between the two support edges. The ratio `v/m_e` eliminates the common
Planck and squash factors and gives a monotone inverse for the endpoint;
an independent matched-ratio interval can therefore constrain the bandwidth.

The DESI scale projection reuses the retained
background and covariance factor. The fixed statistic is `chi2=29.5088`
for thirteen components, with `p=0.00553993`. A logarithmic displacement s
of the common cosmological mass normalization gives
`dln(D/r_d)/ds ~= -0.74496`. The temperature measurement
of Fixsen (2009) restricts s to about 0.00063 at three standard deviations;
the smallest linearized BAO statistic in that interval is 28.20.
Optional theoretical covariances carry
their own source, approximation order and likelihood assumptions.

## Validation map

| Calculation | Independent checks |
|---|---|
| Spectra, endpoint and condensate | Representation dimensions; signed/projected spinor spectra; rough-TT and three-branch response spectra; leading heat coefficient; adaptive frequency integration; complete conformal resolvents; outward root/mass bounds and continuum tails |
| Finite carriers and mode operations | Full connector resolvents; exact chiral anomalies; complete Clebsch--Gordan products; Haar identities; Duhamel responses; Gram normalization and basis covariance |
| Matter and running | Canonical vertices; common flavour normalization; threshold direction; local beta functions; RK4 order and independent reciprocal-variable integration; finite electroweak matching; correlated running-mass combinations and their one-loop scale derivatives |
| Weak and thermal evolution | Analytic free decay; independently integrated inverse rates; detailed balance; thermal limits; baryon/charge stoichiometry; sourced nuclear/weak evolution |
| Gravity and local sources | Physical polarizations and Ward identities; reflection forms; inverse-response matching; conserved-source exchange; finite source differencing; manufactured and radial local solutions; constrained clock/dust kinetic form and exact finite-mode evolution |
| Cosmological propagation | Complete input and configuration identity; resolved thermal species and density budget; neutrino mass/density round trips; independent distance quadrature; covariance and fixed-parameter statistic; common mass-scale response with an independent temperature constraint |

`tests/test_spectral_contracts.py` covers the spectral and interval
contracts, including independent high-precision bubble dispersion
integrals. `tests/test_matter_extensions.py` covers finite source,
spatial matching, running, renormalization and thermal interfaces.
`tests/test_gravity_extensions.py` checks gravity and local response
without invoking store-writing entry points. `tests/test_joint_response.py`
checks the mass relation and joint covariance;
`tests/test_response_domains.py` checks bandwidth derivatives and the
uniform platform; `tests/test_propagation.py` checks the local material-flow
energy and force, background-only solver dispatch, response differencing
and reuse of retained propagation points. The remaining test modules
cover the production sectors, provenance, comparison isolation and release
interfaces. Test parameters and tolerances are explicit in each test.

For individual source and store checks:

```powershell
py scripts/audit_param_writers.py
py scripts/audit_observation_leakage.py
py scripts/audit_numeric_precision.py
py scripts/audit_path_portability.py
py scripts/audit_lean_sources.py
py -m pytest -q -p no:cacheprovider
py scripts/verify_lean_archive.py --lean-exe <path-to-lean.exe>
```

## External propagation and comparison

The ordinary reproduction validates and reuses completed CAMB propagation.
It evaluates the BAO likelihood from the retained distances and registered
covariance, and the SPARC statistics from the registered mass models and
fixed response. The current CAMB record contains the thermal background,
drag sound horizon and distances. It contains no matter power spectrum,
`sigma8` or `S8`. To calculate this background and its physical-input response:

```powershell
py scripts/run_explicit_camb.py --mode background --accuracy 2
py scripts/run_explicit_camb.py --reuse-center --background-response --response-coordinates YHe,omega_b,omega_m,TCMB,N_eff,H0,neutrino_mass_scale --response-refine TCMB,omega_m
py scripts/run_bao_comparison.py
```

The response holds the other physical coordinates fixed while varying
`YHe`, `omega_b`, `omega_m`, `TCMB`, `N_eff`, `H0` and the common
neutrino mass scale symmetrically in their logarithms. The center is reused.
Fourteen thermal-background probes give the seven central differences;
four further probes halve the step for `TCMB`
and `omega_m`. Each probe performs one thermal-background solve and no
perturbation solve. The center additionally requires one density
initialization. These operation counts, all eighteen retained stencil
points and the finite-difference convergence checks are stored with the
response. The resulting elasticities describe local physical-coordinate
dependence; a shared-input direction uses the corresponding chain-rule
coefficients explicitly supplied by the caller.

The complete perturbation and matter-power calculation remains available:

```powershell
py scripts/run_explicit_camb.py --mode full --accuracy 2
py scripts/run_bao_comparison.py
```

Each explicit calculation replaces the unified current propagation record.
Background and full calculations have distinct configuration identities;
matter-power outputs are present only after a completed full calculation.
Both modes use CAMB's compiled atomic constants in the recombination
calculation. The generated electron mass and fine-structure constant are
not runtime inputs to the installed recombination interface; this convention
is recorded with the propagation.

The stored direct HYREC atomic-response calculation has a separate solver
identity and propagates the generated electron mass and fine-structure constant.
Its finite thermal-history response is documented in the framework ledger.
The two commands above reproduce the CAMB propagation; the HYREC response
is evaluated by `evaluate_hyrec_atomic_response` in the thermal interface
with its explicitly supplied runtime and background. Standard verification
checks the stored response's inputs, implementation and solver-resource
fingerprints before reuse.

CAMB requires its optional solver dependency and the declared runtime
configuration. Its resolved solver version, physical inputs, accuracy
settings and execution identity remain attached to the registered result.
The BAO observation vector and covariance are comparison inputs; its
predictions and statistic are derived comparison records. A missing or
mismatched saved calculation is reported as pending.

## Dashboard

To regenerate the dependency and comparison page:

```powershell
py scripts/make_reviewer_dashboard.py
```

Open `docs/reviewer_dashboard.html`. The page presents the stored calculation
and its input-bound comparisons. Its verification state is read from the
structured manifest and applies only when the associated fingerprints match;
generating the page does not rerun the scientific audits.
