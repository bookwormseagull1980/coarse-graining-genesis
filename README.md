# Coarse-Graining Genesis Framework V5

Version 5.0.2.

[![CI](https://github.com/bookwormseagull1980/coarse-graining-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/bookwormseagull1980/coarse-graining-genesis/actions/workflows/ci.yml)
[![Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22067005.svg)](https://doi.org/10.5281/zenodo.22067005)

The canonical DOI for the V5 release series is
[10.5281/zenodo.22067005](https://doi.org/10.5281/zenodo.22067005).
It resolves to the latest published version; the Git tag identifies the exact
source revision used for a calculation.

Author: Jinku Guo, Northwestern Polytechnical University, Xi'an 710072, China.
Email: guojk@nwpu.edu.cn. ORCID: [0009-0000-6600-6171](https://orcid.org/0009-0000-6600-6171).

## Research overview

### Executing the common generating chain

The Coarse-Graining Genesis Framework V5 is the computational implementation of a generating approach to mathematical physics. Its common source is minimal unbiased compositional change, realized through the Gaussian and compact spectral construction. It evaluates the resulting chain through gauge response, mass scales, effective couplings and cosmological readouts. Each quantity is accompanied by a definition and its upstream dependencies, so a numerical result can be followed back through the construction that produces it.

This makes V5 more than a catalogue of output values. Source normalizations, shared endpoints, representation factors, unit conversions and approximation prescriptions enter a dependency structure. A change to one shared input is propagated to the quantities that depend on it. Experimental reference data are maintained as comparison data, allowing the consequences of the generated relations to be examined without feeding the comparison residual back into their source definitions.

### Structural and numerical outputs

The implementation realizes the canonical matter bundle with its sixteen-dimensional complex fibre and the normalized spectral responses used by the gauge-matter construction. Source support and screening conditions select the integer domain $R=5$. The tensor endpoint is evaluated from the same eight-branch response used in the analytic derivation.

An exact change of variable reduces that response to a positive coefficient divided by $c=kL$. One outward enclosure of the coefficient determines both the root and its derivative. The saved rational certificate gives

$$
2.493533986626\le kL\le2.493534629628,
$$

with width $6.43002\times10^{-7}$. Its floating-point center is approximately 2.4935343325. Shared endpoint dependence is retained when this enclosure is propagated to derived quantities. In the recorded calculation the induced relative interval width for the electron mass is about $1.28601\times10^{-5}$.

The generated Yang-Mills calculation includes the positive collective radial response and the complete coexact connection sector. It evaluates the equilibrium gap and the curvature response of the defined generated operator. Retaining the complete response has a measurable numerical effect. The current release records a curvature-variance excess of about 11.42 percent and an integrated-memory excess of about 5.77 percent over the radial replacement. These calculations make the information lost in a scalar reduction directly visible.

Particle-sector outputs include mass-transfer relations, gauge normalization, finite electroweak matching and decay readouts. Cosmological calculations include homogeneous backgrounds, neutrino-related normalization tests, perturbation outputs and primordial-abundance estimates. Their shared inputs make it possible to examine correlations across sectors and locate the source of a discrepancy.

### Numerical evidence with a defined meaning

V5 separates numerical centers, rigorous interval records, perturbative approximations and comparisons with reference data. The endpoint enclosure is a rational certificate with explicit quadrature and tail control. Propagated intervals preserve the dependence on that endpoint. Multi-input physical readouts retain their own matching and approximation information.

The release also records the coverage of its interval calculations. This makes a precise uncertainty assessment possible for each quantity. A displayed center can be used as a reproducible numerical result, while a certified interval carries the stronger enclosure statement supplied by its construction. The two forms of evidence remain distinguishable throughout the output.

The current numerical record includes $\sigma_8$ near 0.81233 and $S_8$ near 0.83226 from the stated cosmological calculation. Nuclear and abundance outputs carry their associated finite-rate and spectral-input information. Cross-sector comparisons can therefore be reproduced and assessed at their actual approximation level.

### Connection to formal proof

V5 and the Lean foundation library supply complementary forms of evidence. Lean declarations prove the indexed source, arithmetic and physical-interface theorems under their explicit formal definitions. V5 evaluates the finite spectral integrals, fixed points, matrix elements and observational mappings associated with those constructions. Structural certificates connect selected executable quantities to the corresponding mathematical identities.

This division makes the full research chain inspectable. A structural theorem establishes the object and its properties. An executable definition fixes the finite calculation. A numerical certificate controls the enclosed quantity. A physical comparison then tests the stated interpretation and matching prescription.

### What the framework contributes

V5 turns a broad generating construction into a reproducible quantitative system. Its principal achievements are the common dependency chain, the selected spectral domain, the certified tensor endpoint, the generated Yang-Mills gap calculation, linked particle and cosmological readouts, and explicit sensitivity to retained response channels.

The strongest advantage is the ability to follow a result across mathematical, numerical and physical layers. Shared origins create testable relations, and recorded dependencies make their consequences visible. V5 provides the computational means to study those relations with finite calculations whose definitions, precision and comparison data can be examined independently.

### Computational entry points

The executable source contract is
`cg_core.content_response.closed_generated_world_contract`. Its canonical
generated realization supplies the source record and physical sectors. Probes
are response coordinates, subsystem boundaries retain complementary state
information, and observational records supply dimensional units or comparisons.

The concrete matter bundle is built by
`cg_core.canonical_matter_bundle.generated_matter_bundle()`. Its base is the
generated Hermitian four-carrier, its fibre is the complete sixteen-coordinate
source matter carrier, and relative frames use the source action. The transition
cocycle and component compatibility are proved in the companion Lean module
`Physical.CanonicalMatterBundle`. That cross-reference identifies the formal
result; the V5 numerical build remains independent of the Lean repository.

## Numerical evidence in the release

The current release record is version `5.0.2`, run
`20261025T021453Z-a4c66902`, with `262` parameter records, `261` derived
records and `0` pending records. It records `648` passing CI-core tests in a
separate check; the complete test suite was not rerun for that record. The
canonical numerical and verification facts are collected in
[RELEASE_FACTS.md](docs/RELEASE_FACTS.md).

The V5 records expose the numbers rather than hiding them behind a model label:

- one finite Gaussian response domain, `R=5`, with the certified active-window
  threshold `R_* ~= 4.0187119842`;
- a cached strict TT endpoint certificate: root bracket
  `[1246766993313/500000000000, 623383657407/250000000000]`, endpoint sign change and a strictly
  negative interval derivative proving uniqueness;
- an exact branch-reduction certificate: the full active V5 TT spectrum is
  exactly the eight branches used by the companion Lean coefficient model,
  and `c*A_V5(c)` equals that coefficient interval;
- a common source and matching ledger for the endpoint, effective couplings,
  mass scales, tensor response and cosmological propagation;
- generated neutron--proton difference `1.28497 MeV`, free lifetime `915.54 s`
  and helium baryon fraction `Yp=0.246082`;
- fixed-input DESI comparison `chi2=29.5087`, `p=0.00554011`, and the direct
  HYREC realization at the archived fixed background,
  `r_d=147.07455 Mpc`, `chi2=27.1191`
  ([calculation archive](https://github.com/bookwormseagull1980/coarse-graining-genesis/tree/4962752ee7edbc722c1a19c636327870d40900e6));
- `16` explicit interval records, `8` production records with an attached
  interval, and `160` centre-only records. No full covariance or fabricated
  model-error envelope is published; see [PRECISION_BUDGET.md](docs/PRECISION_BUDGET.md).

These are calculated records, not independently fitted observational inputs.
Reference observations and covariance matrices remain in a separate comparison
store, and no hidden comparison value is written back into the production
parameters. Every number above can be traced to its source, units and stated
approximation through `cg_params.json` and the verification report.

## Scientific references

The framework implements the constructions listed below. Full bibliographic
entries are given in [REFERENCES.md](REFERENCES.md).

| Reference | Subject relevant to this software |
|---|---|
| Guo (2026f) | Macroscopic gravitational source response, physical tensor spectrum and effective action |
| Guo (2026b) | Classification of long-range correlation channels and source projections |
| Guo (2026d) | Compact internal response space, gauge structure, matter carrier and scalar spectrum |
| Guo (2026g) | Spectral endpoint, effective couplings, mass relations and numerical comparisons |
| Guo (2026e) | Minimal unbiased change and the mathematical generation of the spectral structure |
| Guo (2026h) | Coarse-grained dynamics and certification of resolved macroscopic evolution |
| Guo (2026c, 2026a) | Generated spectral dynamics and certified spectral computation |

The papers state the mathematical hypotheses and physical response definitions. This
repository provides their numerical realizations, finite algebraic checks and
specified source-response calculations. Each calculation identifies its source,
normalization, units, scale and approximation.

## Calculation and results

The production chain evaluates the mode responses on the finite Gaussian
response domain `R=5`, solves the endpoint, assigns the common coupling
boundaries, integrates the scale transfers and evaluates the mass relations.
It also computes the common cosmological budget and the macroscopic tensor
coefficients. The generated records retain their input dependencies.

### Radii: four different objects (do not conflate)

| object | meaning | value |
|---|---|---:|
| `R=5` | finite response-domain **level** `q^2 < R*Lambda^2` | `5` |
| `kL` | V5 **TT endpoint** internal radius: root of `A(L)=4/27` | `2.4935343325...` |
| `sqrt(2*pi)` | Gaussian correlation window **IR edge**; Lean's `CanonicalYangMills` IR-edge model uses it | `2.5066282746...` |
| `sqrt(pi)` | critical endpoint **ratio** `ir/uv`, not an edge | `1.7724538509...` |

`kL` and `sqrt(2*pi)` are **not** the same scale.  At the IR edge the TT sum
is about `0.147374`, below `4/27`; the edge does not satisfy the V5 endpoint
equation.  Production V5 uses `kL`; the Lean zero-argument canonical entry
uses the IR edge.  The two closures are kept separate and must not be
substituted for one another.  See `cg_frg/frg/endpoint_constraint.py` and
`cg_frg/frg/tt_response_domain.py`.

Joint diagnostics evaluate the geometric six-mass relation, its shared-input
derivatives, and the correlated change of electron and electroweak scales
with response bandwidth. The active shell support and three-position condition
give `R_* < R <= 16/pi`, where `c(R_*)=sqrt(11/2)` and
`R_* ~= 4.0187119842`. The ratio `v/m_e` eliminates the common Planck
and squash factors and identifies the endpoint monotonically. The charged-lepton
combination `m_mu^2/(m_e*m_tau)=exp(sqrt(2*pi))` also eliminates the endpoint.
The seven correlated running masses of Huang and Zhou (2021) constrain the
two weighted finite-matching combinations to `Delta_F=2.69537 +/- 1.48017`
and `Delta_L=0.0112736 +/- 0.0005817`. Physical comparisons retain the
mass schemes, scales, matching factors and their joint covariance.
The finite one-loop lepton transfer reduces the common running path
to one weighted integral and supports outward interval bounds. The
remaining matching coefficients satisfy a sharp logarithmic
flavour-spread constraint after the calculated conversion terms.
In the specified `G_l=1` pole-condition realization, the same electroweak action
gives the one-loop pole-to-running combination `Delta_D=0.009337517754`, including
a finite weak contribution `2.348914726e-6`. Its numerical enclosure and
perturbative order accompany the result; no reference mass fixes its inputs.

The matter calculation includes the charged finite carrier, exact anomaly
coefficients, complete spatial mode products, canonical vertices and family
mixing. Conditional five-coupling flows and finite on-shell/MSbar matching use
the actions, schemes and boundary conditions recorded with their results.
The neutrino records identify the three static masses and distinguish their
mass-squared differences from the additional propagation readout.

The colour sector now publishes the full generated Yang--Mills theorem
certificate.  The unique condensed conformal response fixes the radial
intensity block, while the generated projective geometry supplies the complete
positive-odd coclosed colour-connection tower.  Their orthogonal direct sum has
the strictly positive bottom
`Delta_YM^2=min(m_rad^2,m_perp,1^2)`.  V5 evaluates the radial mass by two
independent routes, verifies the radial/constant-mode semigroup intertwiner,
checks higher coclosed shells against the degree-one bottom, and supplies an
outward interval lower bound.  The dimensionless bottom is then transported
covariantly to every positive generated scale.  The endpoint generator scale,
QCD scale and scalar glueball catalogue are the corresponding scale and
composite-state readouts of this same generated colour sector.

### Generated Yang--Mills mass gap

V5 proves, within its executable certificate system, the **generated
Yang--Mills mass gap** as a positive spectral bottom of the generated
Yang--Mills mass operator:

\[
\Delta_{\rm YM}^2>0,\qquad
m_{\rm YM}=\sqrt{\Delta_{\rm YM}^2}\,M_G
=5.940431\times10^{19}\ {\rm GeV}.
\]

The chain certifies the radial and complete coclosed colour-connection
blocks, their self-adjoint Hessian, the positive bottom and the finite Fock
gap; `capacity_closure` records the outward interval lower bound and
`generated_ym_gap_mass` records the mass.

**V5 certifies a strictly positive, attained spectral bottom for the generated Yang--Mills operator at the TT endpoint. The companion Lean library proves the generated IR-edge operator theorem.**

The solved operator is the generated finite Yang--Mills operator.  The Lean
zero-argument theorem proves the IR-edge generated operator; V5 computes the
TT-endpoint generated gap.  The two ends are joined, where the TT coefficient
is concerned, by the exact V5 `tt_branch_reduction` certificate.  The
low-energy glueball catalogue mass `m_glueball=8*Lambda_QCD=1.664 GeV` is a
separate effective readout.

Electroweak partial widths use one effective neutral-current amplitude,
with a common weak angle and normalization, heavy-top bottom-vertex
interference, and factorized QCD and QED radiators. The partial widths
determine the total width, branching ratios and peak cross section at
this same approximation order.

The nucleon source record combines the common proton mass, scalar-isovector
coefficient and electromagnetic mass separation. The BBN approximation
propagates the neutron and proton fractions with conserved total baryon
number and evaluates helium under complete neutron capture. Renormalized
nucleon matching accepts sourced matrix elements and quark masses in a
common scheme and scale; continuous weak evolution and nuclear reactions
use the explicit thermal and reaction inputs described in the ledger.
The common chain gives a neutron-proton difference of 1.28497 MeV,
a free lifetime of 915.54 s and a helium baryon fraction of 0.246082.
The registered PDG 2024 lifetime is 878.4 +/- 0.5 s. The lifetime and
helium central residuals are +4.23% and +0.44%; their common-input
Jacobian retains the hadronic, electromagnetic and weak-rate correlations.
The lifetime elasticity to the mass difference is -6.53633. A comparison-only
diagnostic substitutes the registered experimental mass difference throughout
phase space, freeze-out and decay, giving 877.58790 s and Yp=0.24071583.
It reuses the generated baseline and records the external-input uncertainty
separately from numerical quadrature estimates and physical approximation
errors. The diagnostic is nested in the joint comparison response and does
not supply production inputs.

An independent lattice QCD+QED total splitting is also propagated through
this same weak chain. Its statistical and systematic errors retain their
published separation; finite lifetime and helium ranges follow monotone
phase-space factors and positive survival bounds. Seven distinct mass-gap
evaluations cover the centre and all interval endpoints. The inherited
three-quark colour carrier has one singlet and two independent adjoint
source channels. The actual matter vertex also couples the lowest spinor
shell to both branches of the next shell. These finite carrier calculations
identify the channels entering a dynamical nucleon matching; the scalar
charge requires their constrained bound-state resolvent.

Gravity is represented by a macroscopic collective tensor field. The specified
quadratic Fierz-Pauli action has two physical massless helicities and positive
residue. Matching its inverse source response to the internal critical branch
gives the critical coordinate and external momentum conversion. The common
Einstein--scalar action supplies the nonlinear interaction and conserved
matter coupling. Cosmological evolution and the local static equation use
their stated background, source and boundary data.
Within the unit-normalized first-order quadratic-plus-cubic density class,
affine-dilation covariance fixes the relative cubic coefficient to one.
`affine_dilation_completion()` evaluates the detecting variation in exact
rational arithmetic; the companion Lean physical branch proves the derivative
identity for every local configuration and uniqueness within that class. This
is a documentary cross-reference, not a V5 build dependency. The full
local-coordinate covariance and nonlinear metric field equations are separate
proof targets.
The internal conformal source has a canonical matter evolution with
kinetic weight `M=exp(-3 eta)` and spatial form
`B=exp(-eta/2) A exp(-eta/2)`. Their normalized frequencies reproduce
the static spectral energy. The calculation transports the full canonical
phase covariance, evaluates the causal response including its direct
source term, and checks energy exchange with the varying source.
Both matter quadratic forms are positive. The common covariant realization
below supplies the collective source equation and metric constraints.
The covariant source interface computes the Hilbert stress, internal-source
force and their exact energy-momentum exchange. Its ADM form supplies the
matter lapse and shift sources from the same kinetic and spatial matrices.
A uniform compression is related to a lapse by a canonical dilation,
including the moving-basis coupling and its primary constraint. The
collective source equations balance the calculated matter force.
The phase of an existing pair of equal-mass real coordinates defines a
timelike congruence, `u_mu=-partial_mu(theta)/sqrt(X)` with
`X=-g^ab partial_a(theta) partial_b(theta)>0`. Its time direction is
read from the evolving matter phase. Exact polar equations give its mass-gradient
acceleration, source exchange and radial derivative corrections. Local
checks include homogeneous expansion and an accelerated static phase.
The complete relative condensate potential also has a joint amplitude
and radius minimum. With its fixed subtraction and coupling, it selects
`L_star=sqrt(2)*Lc` and has a positive joint Hessian. The relaxed radius
response is certified from one stationary interval and its spectral tail.
The occupied covariant realization combines this potential with the positive
radial kinetic term, the retained matter pair and the Einstein action.
The collective radius is fixed algebraically by `U_eta+3T-V=0` at each
state. Explicit nonzero occupied initial data satisfy this balance and
the Friedmann constraint; matter, radius and geometry then evolve together.
After eliminating the radius, lapse and shift, the scalar kinetic form is
`K=diag(Z,M,M)+b*b^T/h` with `h=U_etaeta-9T+V`. Its positive branch has
two unit scalar characteristic speeds and
`c_parallel^2=h/(h+18T)>0`, together with the two Einstein tensor modes.
The conserved matter phase charge provides the proper-time readout on
the same solution. The stored calculation includes constraint residuals,
propagation coefficients and operation counts for this occupied background.
A continuous interval certificate proves the source and kinetic conditions
for `0 <= mu*s <= 0.01`, with a squared characteristic-speed lower bound
above `0.1918`. It uses eight spectral endpoint evaluations and an
exit-time bound; the longer numerical trajectory is recorded separately.
The same interval also supports a certified source-reuse calculation.
Piecewise-linear canonical trajectories share one action and initial
state. A positive canonical source curvature converts each bounded
source residual into a trajectory defect, controlling the scale factor,
internal radius and phase readout over the complete interval. Spectral
values and derivatives are retained between accepted source refreshes.
The calculation records source solves, residual checks, spectral work
and outward-interval arithmetic, including the common setup.
The same auxiliary-radius action admits nonuniform plane-symmetric initial
data satisfying its Hamiltonian and momentum constraints. The radius is
solved from the local source balance at every evolved state. Spatial and
temporal refinements record the constraints, phase-clock domain and reduced
propagation matrices. The finite numerical trajectory accompanies a local
existence result on the positive-curvature branch. Its short-distance
metric response has the Einstein--Poisson principal part.
An optional effective realization uses an independent foliation field to
place the static RMS response and the geodesic Einstein branch in one
covariant action. Its reduced scalar action
on a dust and constant-vacuum background has positive quadratic kinetic
coefficients for both the total cold-source mode and the relative clock.
Finite mode evolutions check the conserved foliation charge and the Einstein
evolution of the total cold source. The construction uses the foliation
formalism of Blanchet and Marsat (2011); Blanchet and Skordis (2024) provide
a related relativistic treatment of local and cosmological responses.
For accelerated static backgrounds, eliminating the potential gives
`K=2 M_P^2 B^T(D L^-1 D-D)B` on supplied generated directions `B`.
The calculation solves all source columns with one response factorization
and reports the kinetic spectrum relative to their gradient metric.
The independent foliation has a negative longitudinal velocity direction
above `|grad(Phi)|/a0=sqrt((sqrt(5)-1)/2)`. A radial reduction identifies
the corresponding shell around a spherical source. An invariant-subsystem
realization of this effective action is tested on its generated image,
preserving the parent action's constraints and evolution. A variational
pullback is reduced using the constraints of the pulled-back action.
For a native generated action,
the physical kinetic form is obtained from that action's own constraint
reduction, including all matter, metric and source cross terms.
For supplied reduced matrices and a total normalized operator error bound,
the finite kinetic certificate reports a positive lower bound, a negative
direction, or an unresolved interval. Its record identifies the action,
physical variation space and source map used in that calculation.
An invertible Gaussian change within one retained span preserves its
inertia; restriction to a generated physical subspace additionally uses
the actual source map and evolution.
The local nonlinear potential also drives a finite plane-symmetric material
flow derived from the nonrelativistic source--potential action. The calculation checks mass conservation,
energy balance with boundary work, and time-step convergence before crossing.
The local static and material-flow calculations use this variational flux
directly. CAMB and DESI use the stated Einstein--matter thermal background;
the independent foliation field is not an input to either calculation.
The local-flow checks and the independent-foliation consistency checks are
reported separately. The latter test the action's identities and mode
solutions, including its negative accelerated-background coefficient.
An expanding periodic realization varies the homogeneous lapse, scale
factor and cold displacement in the same nonrelativistic response action.
The complete one-dimensional RMS potential is eliminated by its exact
flux law. The resulting constrained Hamiltonian supplies the background
feedback and a positive physical kinetic coefficient on a finite interval.
Its homogeneous limit gives the dust--vacuum Friedmann equation; freezing
the expansion retains the same local nonlinear constitutive law. The
remaining spatial approximation is the displacement window, whose omitted
force is bounded and recorded separately.
The same canonical states supply density, velocity, expansion and weak-field
material-clock readings. Their uniform bounds use the existing rational
exit box. Saved-state derivatives and readings share one reconstructed
potential; the clock bounds add no field solve or trajectory step.

Scientific values, complete operator and matching evaluations, interval
certificates and fixed-input propagation results are registered in
`cg_params.json`. Each record retains the conditions needed to interpret
and reproduce it. Reference observations and covariances are kept separately
in `comparison/reference_inputs.json`.

These are the two authoritative scientific stores. Calculation modules
use the common parameter interface, with checked prediction reads and
separate reference-data access. Solver settings are registered with their
comparison data. Reusable calculations are read from `cg_params.json`
after their inputs and implementation have been validated.

CAMB propagates the fixed endpoint input set. The Friedmann constraint
resolves the nonbaryonic endpoint budget into the cold component, photons
and thermal neutrinos. The propagation and subsequent DESI BAO comparison
retain their complete configurations and data identities. The calculated
statistics are available in the parameter store and generated reviewer
dashboard.
The fixed thirteen-component DESI comparison gives `chi2=29.5087`
and `p=0.00554011`. A common cosmological mass-normalization direction
has distance-ratio elasticity approximately `-0.74496`. Combining that
direction with the independent CMB temperature of Fixsen (2009) permits
only about `0.00063` in logarithmic normalization at three standard
deviations; the smallest linearized BAO statistic in this interval is
`28.20`. These correlated diagnostics retain the fixed production inputs.
Finite thermal scaling gives an exact common distance multiplier in
the stated background approximation. At fixed drag epoch the statistic
is at least `28.6237`; reaching the 95-percent reference level requires
a further logarithmic drag-integral response of at least `0.00258406`.
These bounds reuse the saved covariance projection and background data.
Direct HYREC full radiative-transfer evolution also propagates the generated
fine-structure constant and electron mass through the atomic rates and
Thomson opacity at the same expansion history. It gives a drag sound horizon
of 147.07455 Mpc and a thirteen-distance statistic of 27.1191. A finite
electron-number bound covering all ionization changes below redshift 30
gives a statistic range [25.7794, 28.5175] around this atomic realization.
The higher-redshift atomic and radiative-transfer remainder is a separate
physical uncertainty. The calculation retains solver-resource fingerprints
and evaluates no power spectra; subsequent verification reuses its saved
result after checking the background and atomic inputs.

## Documentation and reproduction

### Quick start

Run the self-contained spectral smoke test first:

```powershell
py examples/quickstart/run_example.py
```

It generates a three-shell scalar record on the `RP3` carrier and checks the
stored output values. The example completes without optional cosmology
solvers. Then run the explicit finite response-domain endpoint certificate:

```powershell
py scripts/certify_tt_response.py
```

It prints `c(4)`, `c(5)`, `c(6)`, the lower platform edge `R_*`, and the unique
integer level in `(R_*, 16/pi]`; the upper edge is the shell-support bound, not
the `c(6)` crossing. Then run the core regression suite:

```powershell
py -m pip install -r requirements-lock.txt
py -m pytest -q -m "not numerical and not auxiliary" -p no:cacheprovider
```

`requirements-lock.txt` records the tested Python 3.13.12 environment;
`requirements.txt` gives compatible lower bounds for ordinary installation.
Both include CAMB 2.0.5, and `scripts/reproduce_v5.py` runs the full endpoint
power-spectrum record automatically. For a full release
verification, including fresh reproduction and audits, use the command in
[REVIEWER_START_HERE.md](REVIEWER_START_HERE.md). The CI workflow
runs the core suite on every push and pull request; it is a public regression
check, not a substitute for the full release verification.

- [Release facts](docs/RELEASE_FACTS.md): canonical counts, run identity,
  endpoint/interval widths and the YM/Lean snapshot.
- [Scientific overview](docs/papers_overview.pdf): construction, selected results,
  macroscopic dynamics and the interpretation of the comparisons.
- [Papers index](docs/PAPERS.md): all companion PDFs and popular introductions.
- [Framework ledger](docs/V5_LEDGER.md): spectral construction, effective
  couplings, finite matching, thermal evolution, gravity and cosmology,
  with their assumptions, normalizations and error controls.
- [Structural closure](docs/STRUCTURAL_CLOSURE.md): executable certificate
  chain and the exact TT branch reduction.
- [TT equivalence](docs/TT_EQUIVALENCE.md): the V5-to-Lean eight-branch identity.
- [Lean correspondence](docs/LEAN_CORRESPONDENCE.md): what the Lean physical
  branch proves, what is certificate-conditional, and the YM mass-gap scope.
- [Precision budget](docs/PRECISION_BUDGET.md): endpoint/BBN intervals and the
  centre-only record boundary.
- [Scope and limits](docs/SCOPE_AND_LIMITS.md): what is solved, what is
  effective, and why no traditional 4D QCD quantum field is constructed.
- [Changelog](CHANGELOG.md): the 5.0.2 release delta.
- [Completeness audit](V5_COMPLETENESS_AUDIT.md): final state and residual
  numerical boundaries.
- [Reviewer guide](REVIEWER_START_HERE.md): installation, reproduction,
  test and formal-verification commands, and the validation map.
- [Verification report](V5_VERIFICATION_REPORT.md): executed checks and
  their scope for the identified calculation.
- [Reviewer dashboard](docs/reviewer_dashboard.html): stored dependencies,
  calculated quantities and observational comparisons.

The source/output manifest binds the calculation and its verification
state to the distributed files. Matching external propagation is reused
after input and configuration validation. Spectral certification reuses
root intervals and trajectory data where the mathematical bounds permit.
Computational work is recorded as operation counts. Each response is bound
to its transitive source dependencies and actual inputs. Shared numerical
examples are evaluated once per test module; independent formulas and
refinement calculations supply separate checks.
The manifest contains identity and verification metadata; scientific
inputs and calculated values are supplied by the two stores above.

The source distribution includes the verification suite. Runtime installation
requires only the calculation dependencies. The reviewer guide distinguishes
core algebra and isolation checks, extended numerical certification, and
auxiliary presentation checks. Full verification is used for release;
targeted tests cover changes to individual sectors.

V5 is self-contained. Its numerical chain does not import or require the
separate Lean physical branch. V5 carries its own finite Lean archive in
`lean_proofs/` for selected integer/rational identities, and its structural
chain is recorded by the executable certificates in `cg_core/structure/`:
minimal change -> Gaussian endpoints -> internal spectra -> content capacity
-> endpoint root and Yang--Mills capacity. These certificates are V5-local and do not
claim to be Lean formal proofs of the full structural theorems.

The `certificates/structure_certificates.json` record is regenerated by
`py scripts/structure_certificates.py` and by the full reproduction chain.
The ordinary V5 calculation and test imports do not require any external
proof checkout.

The companion Lean physical branch proves the generated **IR-edge**
Yang--Mills mass gap.  Its `SourceTTGaussianCoefficient` uses eight active
branches with response `A_5/c`.  V5 certifies that the **full** active finite
spectrum on the endpoint bracket is exactly those eight branches and that
`c*A_V5(c)` equals the same coefficient interval; the certificate is
`cg_core/tt_branch_reduction.py`.  The Lean root theorem therefore applies to
the V5 full response as an exact model reduction, not a numerical
approximation.  The bridge is a V5 certificate/table identity, not a Lean
import.  The full derivation is in [TT_EQUIVALENCE.md](docs/TT_EQUIVALENCE.md).
V5's strict endpoint certificate and generated Yang--Mills gap remain
self-contained.

**The generated Yang--Mills mass gap is solved.  There is no traditional 4D
QCD quantum field to be matched or proved separately**: the conventional 4D
QFT construction cannot construct the 4D quantum field or prove the
Yang--Mills mass gap.  The low-energy glueball catalogue is an effective
readout of the same generated finite operator.
The certified endpoint width and its propagation to the mass scale are
tracked separately in [PRECISION_BUDGET.md](docs/PRECISION_BUDGET.md).

## Repository contents

| Location | Contents |
|---|---|
| `cg_core/` | Parameter definitions, compact spectrum, finite carriers, mode algebra, matching and beta functions |
| `cg_frg/` | Endpoint, coupling, matter, cosmology and macroscopic gravity sectors |
| `scripts/` | Reproduction, verification, certificates, fixed-input comparisons and dashboard generation |
| `tests/` | Independent identities, numerical convergence and software-contract checks |
| `cg_core/structure/` | V5-local structural certificates: minimal change, Gaussian endpoints, internal spectra, content capacity, endpoint root, TT branch reduction and YM capacity |
| `certificates/` | Generated structural and numerical certificates |
| `lean_proofs/` | V5-internal finite integer/rational Lean checks |
| `comparison/` | Observational inputs and post-calculation comparison procedures |
| `docs/` | Release facts, ledger, structural/TT/Lean correspondence, precision/scope, papers index and generated dashboard |
| `MANIFEST.in` | Source-distribution inclusions for tests, scripts, certificates and documentation |
| `V5_COMPLETENESS_AUDIT.md` | Current completeness/rigor audit |
| `V5_VERIFICATION_REPORT.md` | Generated verification evidence for the release run |
| `CHANGELOG.md` | Release delta |
| `cg_params.json` | Unified scientific records and their provenance |
| `run_manifest.json` | Run identity, source/output fingerprints and verification state |
| `CITATION.cff` | Software citation metadata |
| `REFERENCES.md` | Scientific bibliography |

Floating-point central values, outward mathematical enclosures and model
sensitivity have distinct meanings. The framework ledger states their
scope. The Lean archive verifies selected finite implications; the
companion papers give the analytic and physical arguments.

The [variational foundation calculations](docs/V5_VARIATIONAL_FOUNDATIONS.md)
give the complete-carrier torsion response, all three algebraic torsion
sectors and their downstream spectral transfer, the endpoint-profile
variation, and the gauge zero-mode normalization. Run
`py -3.13 scripts/check_variational_foundations.py` for the corresponding
store-independent calculation report.

The finite content equation has positive capacity `50` and the unique
exact solution `tau_content=1/50`. The normalized isotropic connection
lift is implemented without a modulus argument. Run
`py -3.13 scripts/solve_torsion_response.py` to evaluate this fixed-content
lift, or
`py -3.13 scripts/solve_torsion_response.py --content-radius-bracket 1.65 1.95 --cells 256`
for a certified local radius minimum of the displayed curvature/fermion
action restricted to that lift. Independent connection comparisons are
selected explicitly by `--vary-connection` or `--joint-radius-bracket`;
they do not replace the exact content value.

The same calculations now include joint torsion/radius variation with
the reference determinant, internal volume and moving frequency edges
retained. Run
`py -3.13 scripts/solve_torsion_response.py --joint-radius-bracket 1.65 1.95 --cells 256`
to reproduce a certified local stationary point of the stated
trace-matched curvature/fermion action. The report distinguishes this
functional from the published content-response coordinate `tau=1/50`.

## Citation and license

Cite this software as J. Guo, *Coarse-Graining Genesis Framework V5*,
version 5.0.2 (2026), together with the applicable companion papers in
[REFERENCES.md](REFERENCES.md). The version-series DOI is
[10.5281/zenodo.22067005](https://doi.org/10.5281/zenodo.22067005); use the
Git tag `v5.0.2` to identify this exact source revision. Machine-readable
citation information is provided in [CITATION.cff](CITATION.cff).

Source repository:
[coarse-graining-genesis](https://github.com/bookwormseagull1980/coarse-graining-genesis).

The software is released under the standard MIT License in [LICENSE](LICENSE);
the requested citation is recorded separately in [CITATION.cff](CITATION.cff).
