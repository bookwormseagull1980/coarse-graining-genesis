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

# Coarse-Graining Genesis Framework V5

Version 5.0.0.

A reproducible spectral calculation of effective couplings, mass scales and
macroscopic source responses. The calculation starts from the specified compact
internal spectrum, finite matter content and Gaussian response domain. Newton's
constant supplies the observed dimensional anchor; the remaining production
inputs are the structural assumptions and matching conditions stated in the companion
papers.

Author: Jinku Guo, Northwestern Polytechnical University, Xi'an 710072, China.
Email: guojk@nwpu.edu.cn. ORCID: [0009-0000-6600-6171](https://orcid.org/0009-0000-6600-6171).

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
In the generated-pole realization, the same electroweak action gives the
independent one-loop lepton combination `Delta_L=0.009337517754`, including
a finite weak contribution `2.348914726e-6`. Its numerical enclosure and
perturbative order accompany the result; no reference mass fixes its inputs.

The matter calculation includes the charged finite carrier, exact anomaly
coefficients, complete spatial mode products, canonical vertices and family
mixing. Conditional five-coupling flows and finite on-shell/MSbar matching use
the actions, schemes and boundary conditions recorded with their results.
The neutrino records identify the three static masses and distinguish their
mass-squared differences from the additional propagation readout.

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
The fixed thirteen-component DESI comparison gives `chi2=29.5088`
and `p=0.00553993`. A common cosmological mass-normalization direction
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

- [Scientific overview](docs/papers_overview.pdf): construction, selected results,
  macroscopic dynamics and the interpretation of the comparisons.
- Popular introductions: [English](docs/From%20Change%20to%20Everything%20-%20A%20Popular%20Science%20Introduction.docx)
  and [中文](docs/从变化到万物_科普导读.docx).
- [Framework ledger](docs/V5_LEDGER.md): spectral construction, effective
  couplings, finite matching, thermal evolution, gravity and cosmology,
  with their assumptions, normalizations and error controls.
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

The independent proof library *Lean Formalization of Arithmetic and Basic
Physical Interfaces* contains the shared foundations formalized for the
arithmetic and gauge-structure papers. It is maintained separately from V5.
`foundations-reference.json` pins its proof sources, dependency locks and
complete verification program. V5's optional `--foundations` check invokes that
program and binds a newly produced proof record; it does not certify the
numerical calculation or the full mathematical content of the papers.
The ordinary V5 calculation and test imports do not require this library.
See the [reviewer guide](REVIEWER_START_HERE.md) for checkout configuration.

## Repository contents

| Location | Contents |
|---|---|
| `cg_core/` | Parameter definitions, compact spectrum, finite carriers, mode algebra, matching and beta functions |
| `cg_frg/` | Endpoint, coupling, matter, cosmology and macroscopic gravity sectors |
| `scripts/` | Reproduction, verification, certificates, fixed-input comparisons and dashboard generation |
| `tests/` | Independent identities, numerical convergence and software-contract checks |
| `lean_proofs/` | Finite integer/rational formalizations with their declared premises |
| `foundations-reference.json` | Pinned reference to the independently maintained arithmetic and basic-physics proof library |
| `comparison/` | Observational inputs and post-calculation comparison procedures |
| `docs/` | Framework ledger and generated reviewer dashboard |
| `cg_params.json` | Unified scientific records and their provenance |
| `run_manifest.json` | Run identity, source/output fingerprints and verification state |
| `CITATION.cff` | Software citation metadata |
| `REFERENCES.md` | Scientific bibliography |

Floating-point central values, outward mathematical enclosures and model
sensitivity have distinct meanings. The framework ledger states their
scope. The Lean archive verifies selected finite implications; the
companion papers give the analytic and physical arguments.

## Citation and license

Cite this software as J. Guo, *Coarse-Graining Genesis Framework V5*,
version 5.0.0 (2026), together with the applicable companion papers in
[REFERENCES.md](REFERENCES.md). V5 has no assigned DOI. Machine-readable
citation information is provided in [CITATION.cff](CITATION.cff).

Source repository:
[coarse-graining-genesis](https://github.com/bookwormseagull1980/coarse-graining-genesis).

License and attribution terms are provided in [LICENSE](LICENSE).
