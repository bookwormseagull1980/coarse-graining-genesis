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

# V5 Framework Ledger

This document specifies the physical objects, numerical methods and
certification used by Coarse-Graining Genesis Framework V5, version 5.0.2.
The companion papers in [REFERENCES.md](../REFERENCES.md) supply the
derivations. The [reviewer guide](../REVIEWER_START_HERE.md) provides
execution commands and the validation map.

## Current verified calculation

```text
run identity          20261025T021453Z-a4c66902
parameter records     262
DERIVED / PENDING     261 / 0
complete definitions  262/262
Python tests          648 CI-core tests passed separately; full suite not rerun
structural certs      11 PASS
internal Lean archive 18 files
explicit intervals    16
attached intervals    8
centre-only records   160
endpoint bracket      [1246766993313/500000000000, 623383657407/250000000000]
```

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**
The solved operator is the generated finite Yang--Mills operator.  Lean proves
the IR-edge generated gap; V5 computes the TT-endpoint generated gap.  The
low-energy glueball catalogue is a separate effective readout.

Canonical release numbers: [RELEASE_FACTS.md](RELEASE_FACTS.md).  Scope:
[SCOPE_AND_LIMITS.md](SCOPE_AND_LIMITS.md).

- [Data discipline](#data-discipline)
- [Closed-world object discipline](#closed-world-object-discipline)
- [Defining closures](#defining-closures)
- [Spectral construction and certification](#spectral-construction-and-certification)
- [Matter, running and thermal methods](#matter-running-and-thermal-methods)
- [Gravity and cosmology](#gravity-and-cosmology)
- [Verification scope](#verification-scope)

## Data discipline

The two scientific stores are `cg_params.json` for internal parameters
and calculated results, and `comparison/reference_inputs.json` for
external reference data and comparison propagation settings. Every
calculation and registration uses the common parameter interface.
Complete-run reconstruction uses the same file layout in an isolated
directory. Reports and the dashboard are views of these records.

Scientific results are registered once in `cg_params.json` through the
common parameter interface. Scalars, matrices, numerical trajectories,
interval certificates and comparison results use the same publication
interface for role, writer, source identity and run identity. The interface
also records declared physical definitions and direct input dependencies;
the generated report gives their coverage. Each structured response section
binds its direct inputs and retains physical units and conventions in its
payload. Conditional examples retain their supplied action, source,
boundary and approximation data.

The computation distinguishes four layers:

1. `OBSERVED / anchor`: Newton's constant sets the dimensional scale. This
   empirical unit calibration is not a dynamical source of the closed model.
2. Structural derivation: V5-local certificates derive the RP3 carrier from
   the quaternion centre quotient, the content from the primitive trace-free
   charge lattice, the finite response level from the endpoint inequalities,
   and the gauge/flow normalizations from the common Planck normalization and
   unit-speed flow. The projected response and matching conventions remain
   stated model conventions, not fitted parameters.
3. `DERIVED`: scientific records produced by the acyclic calculation.
4. Comparison: observational reference values and covariances in
   `comparison/reference_inputs.json`, used to evaluate the completed calculation.

Fixed-input downstream propagation retains its executed solver version,
resolved configuration and input fingerprints with its scientific result.
A matching completed calculation is reused under its recorded validity
conditions. The comparison role and read protections keep observational
targets separate from production input.

`run_manifest.json` records the run identity, source and output
fingerprints and structured verification status. The verification report
and reviewer dashboard present these records. Current numerical values,
record counts and coverage are read from the store and generated report.
Its storage contract binds exactly these two scientific stores. Reuse
checks the identity of a calculation before reading its value from the
parameter store; the manifest supplies the identity checks only.

## Closed-world object discipline

The dependency graph has exactly one ontological root, minimal unbiased
compositional change.  The zero-argument executable entry
`closed_generated_world_contract()` records that root and verifies the balanced
complete matter capacity.  All parameters below occur only after this root as
generated realization coordinates, internal projections, unit conventions, or
comparison records.

V5 uses four distinct notions that are not interchangeable:

| Term | Meaning | What it does not mean |
| --- | --- | --- |
| complete generated source | the positive joint state containing every retained sector and its common dynamics | a signed center observable |
| quotient or projected source | the state seen after a declared carrier reduction, with its Schur or threshold feedback retained when required | the ontology of the complete carrier |
| applied probe | an optional parameter used to differentiate a response function | a source required to close the generated system |
| interface or comparison datum | boundary data inherited by a subsystem, or an observed value used for units and comparison | an outside-universe dynamical cause |

Accordingly, the complete `8_L+8_R` matter carrier has zero intrinsic center
bias. The `8_L+7_R` value and `tau=1/50` belong to the gauge-active charged
quotient. The historical word `external` in tensor module names means
noncompact relative to the compact internal carrier; that tensor sector is
dynamical and belongs to the same closed action. A finite-window or projected
imbalance is reported as endpoint flux or projection defect, not promoted to
a fundamental source. These distinctions are part of the scientific contract,
not merely terminology.

### Concrete matter bundle

`cg_core.canonical_matter_bundle.generated_matter_bundle()` takes no
realization arguments. It constructs the Hermitian four-coordinate base,
the complete sixteen-coordinate source fibre, its identity frame and the
existing colour, weak and hypercharge matrices. The neutral line is obtained
from the simultaneous kernel of those actual matrices; it is retained in the
complete fibre. For source frame configurations, relative transitions are
`g(x)^(-1) h(x)` and section components transform by the same unitary action.
Their cocycle, norm preservation, component compatibility and faithful-action
uniqueness are proved in `CanonicalMatterBundle.lean`.

The total space here is the product of the already generated base and fibre.
No arbitrary localized bundle is required to instantiate this result.
Coordinate uniqueness means uniqueness preserving these two source
coordinates; it is not a classification of all possible bundle topologies.

## Defining Closures

- The one-loop TT spectral response is
  `K_TT(k^2,m^2)=k^4/(k^2+m^2)^2`; it satisfies
  `K_TT(k^2,0)=1`. The Ward-normalised subtracted flat amplitude is
  recorded separately.
- With `y=m^2/(k^2+m^2)`, the mass-weighted response is
  `y(1-y)^2`. Its unique interior maximum is `4/27` at `y=1/3`;
  the endpoint closure adopts this extremum as its response normalisation.
  The noncompact tensor spectrum is evaluated from its sourced physical action.
- The torsion modulus is the dimensionless charged-quotient response invariant
  `tau=(N_L-N_R)/(N_f SumY2)=1/50`. The complete matter carrier is `8_L+8_R`
  and has zero intrinsic center bias; the neutral right coordinate is absent
  only from the gauge-active trace.
  Equivalently, on all sixteen coordinates it is
  `Tr(P chi)/(Tr(P) Tr(Y^2))`, `P=support(Y)`. The spin-connection
  vertex also acts on the neutral coordinate. In the classical minimal
  internal spin action it sources only the trace of dual torsion;
  the other two sectors eliminate uniquely at the invertible production
  Hessians. Rotational symmetry fixes this isotropic direction but
  allows three independent quadratic-action coefficients. The field
  equation for its amplitude and the downstream spectral derivatives are
  evaluated in `cg_core.ec_variation` and recorded by
  `ec_torsion_sector_contract`. See
  [the action variations and their matching equations](V5_VARIATIONAL_FOUNDATIONS.md).
- The generation capacity is the declared map
  `n+3/2 < (kL)^2` on `n=0,2,4,...`; at the fixed point it returns
  `n=0,2,4`.
- The electron exponent is the content number
  `(d+1)(SumY2 Delta_f)=4*5=20`.
- The neutrino mass matrix assembles the prescribed hypercharge-trace
  eigenvalue texture and PMNS rotation. Diagonalisation verifies the
  assembled texture and its absolute Weinberg scale.

## Spectral construction and certification

### Spectral objects

`cg_core.rp3_spectrum` provides the following distinct objects:

| Interface | Carrier and operator | Lowest eigenvalue / Weyl weight |
| --- | --- | --- |
| `true_tt_modes(L,k_max,operator="rough")` | Two transverse-tracefree branches, C2-6 | 6/L² / 2 |
| `true_tt_modes(...,operator="K6")` | Same true-TT carrier, C2+6 | 18/L² / 2 |
| `response_tensor_modes(L,j_max)` | Three-branch tensor-response catalogue including (j,j), C2+6 | 14/L² / 3 |
| `dirac_modes(L,n_max)` | One spin lift: positive even n, negative odd n | signed D |
| `dirac_squared_modes(...,projection="full")` | All n for D² of that lift | full spinor weight 2 |
| `dirac_squared_modes(...,projection="P_plus"/"P_minus")` | Additional even/odd source projections | each weight 1 |

The `tt_*` symbols evaluate the three-branch tensor-response
catalogue. Its production source projections define the 7/4 window readout
and assigned QCD coefficient 14. These numbers belong to that specified
catalogue. The rough-TT spectrum uses its two-branch carrier and minimum
6/L^2. The `tensor_TT` iterator key selects the three-branch internal tensor-response catalogue.

`spinor_quantum_numbers` returns the half-integer representation labels
whose dimensions equal (n+1)(n+2). `heat_kernel` returns the finite
spectral sum and its proved leading coefficient a0=7 Vol for the three-branch tensor-response
catalogue. Its combined a2/a4 entries are `None`; the supplied heat-trace data consist
of the explicit finite sum and leading Weyl coefficient.

### Complete connectors and actual mode operations

`cg_core.finite_connector` constructs the complete elementary connector on
the specified joint carrier, its chiral block operator, kinetic-normalized
transfer and source/readout response. A charged/neutral split is an explicit
choice of subspace. Schur elimination is used only when the required block
is invertible; the near-zero case retains the full resolvent problem.
Equality to the full source response is checked numerically. A finite unit
connector matrix element fixes the finite-carrier seed normalization. The
spatial Yukawa vertex combines it with the mode overlap and canonical action;
the beta function uses the specified renormalization scheme.

`cg_core.modal_algebra` implements Haar-normalized Clebsch--Gordan products,
matrix-valued mode multiplication, derivatives, curvature and the matter
covariant derivative for a common connection. The joint heat-resolution
defect and its integral/cocycle are evaluated from those actual products.
Their stated domain is fixed radius and frame, with scalar-coefficient heat
resolution. The heat parameter labels internal resolution; physical time
evolution and the effective-action FRG use their stated generators.

The spinor-multiplication interface retains explicit signed input/output
branches. A concrete multiplier gives a nonzero positive/negative branch
overlap, retaining its full matrix-valued source projection.
The Killing carrier `(1,0) + (0,1)` has a 21-dimensional symmetric square,
with Casimir values 0, 8 and 12 of multiplicities 2, 9 and 10. The code also
forms the colour-singlet lift and source projections. These carriers define internal two-body responses. A specified composite
observable and its matching determine their external JPC and hadronic
interpretation.

`evaluate_native_operations()` returns the evaluated finite-operator and
mode-product checks without a store write. The production run registers these explicit examples in `cg_params.json`,
with their prescribed inputs, physical definitions and direct dependencies.

### Exact content source and the joint selection

`cg_core.content_response.finite_source_response()` evaluates the
connected Hessian of the specified five-coordinate finite source:

    gradient = (1/15,0,0,0,0)
    Hessian  = diag(224/225,2/9,2/15,2/15,2/15)
    tau      = (1/15)/(15*(2/9)) = 1/50.

All entries use `Fraction`, without floating-point rounding. Its block
exponential is independently available as `finite_source_log_partition`.
`chiral_anomalies()` verifies LH-minus-RH cubic U(1), gravitational-U(1),
SU(3)²U(1), SU(2)²U(1), SU(3)³ and the even SU(2)-doublet count. Every
coefficient vanishes. The unsigned third moment is -4/9. Anomaly coefficients use the chiral
LH-minus-RH trace stated above.

The charged source acts on the 15-component quotient of Guo's (2026d)
16-component joint module. `screening_compatibility()` uses the same
four-doublet carrier to obtain the extensive response ratio 2/(2g)=1/g.
Together with the specified colour normalization 3 delta=1 it selects
g=3 before an endpoint is evaluated. `sm_content.N_GENERATIONS` and the
production field instantiation use this result. `window_capacity.compute`
then checks the endpoint platform for that selected content.

The missing coordinate in this quotient is not discarded from the joint
matter carrier. It is the right-handed neutral singlet `nu_R`, the explicit
neutral coordinate of `finite_connector.elementary_connector`. The complete
carrier therefore has capacities `8_L+8_R`; only the charged trace has
`8_L+7_R`. The two levels serve different observables:

- `chiral_center_response(neutral_right_weight=1)` evaluates the complete
  center channel and gives zero bias, unit susceptibility, and unit restoring
  Hessian without an applied probe;
- `chiral_center_response(neutral_right_weight=0)` evaluates the charged
  quotient and recovers bias `1/15`, susceptibility `224/225`, and restoring
  Hessian `225/224`;
- eliminating the neutral line in an operator response requires the Schur or
  full solve in `finite_connector.source_response`. The quotient bias is a
  projection defect and is not identified with a fundamental asymmetry of the
  complete carrier.

No external center source is needed to close the generated system.  On the
complete carrier the optional odd-probe partition function is

    Z(h)=(8 exp(h)+8 exp(-h))/16=cosh(h).

It is even, and therefore its logarithmic derivative vanishes exactly at
`h=0`.  `closed_chiral_center_certificate()` records this intrinsic
`8_L+8_R` closure.  The `8_L+7_R` result belongs only to the charged
projection obtained after removing `nu_R`.

For the separate response experiment `h(L)=a(L/L0)^(-alpha)`, the response is
`m=tanh(h+h0)`, where `h0=(1/2)log(N_L/N_R)`. Since `tanh` is one-Lipschitz,
the complete carrier satisfies

    integral_1^infinity m(x)^2 dx/x <= a^2/(2 alpha).

The charged quotient instead has the persistent zero-drive tail `m0=1/15`;
its infinite logarithmic-scale energy diverges, although every declared
finite window has the explicit bound returned by
`chiral_center_power_law_screening`. This optional probe calculation is not a
closure premise.  The distinction prevents a finite charged-window
certificate from being reported as complete-carrier restoration.

For a supplied Hermitian interaction/background K,
`log_partition_response(K,A,J)` evaluates `log Tr exp(K+sum J_a A_a)/n`,
its gradient and the connected Duhamel/Kubo--Mori Hessian. In the energy
basis the Hessian uses the logarithmic mean of the Gibbs probabilities,
including off-diagonal matrix elements. For a noncommuting background and source, the response uses the full
Duhamel form. Shifted exponentials and
divided differences remain stable at degenerate levels and large gaps.

`interacting_content_response` uses the actual five matrices on the charged
carrier. Positive common block weights leave normalized responses invariant;
for relative left/right weight r, the explicitly defined tau response is
`(8r-7)/(10r+40)`. The zero-background structural value is 1/50. The weighted response
quantifies the specified finite-source susceptibility. The external kinetic
coefficient is supplied by the canonical action.

### Spatial Gram, vertex and canonical normalization

`cg_core.matter_matching` integrates supplied bundle-valued spatial modes,
their kinetic metric and the actual Higgs/operator insertion. The measure and all spinor-bundle components enter the stated vertex. Positive kinetic Grams give the canonical vertex
`Z_L^(-1/2) Y Z_R^(-1/2)/sqrt(Z_H)`. General invertible mode changes induce
unitary changes of the canonical bases: singular values and physical amplitudes are invariant. Canonical
normalization acts on the resolved positive kinetic subspace. The interface
rejects null or unresolved modes and checks spatial quadrature convergence.

One-form and two-form Gram contractions are separate. For the fixed axial
Killing vector and `A=1+s`, `B=1-2s`, its dual is `B*sigma3`; the program
evaluates internal-curvature norm ratio `B^(5/2)/A` and external-amplitude
one-form norm ratio `A*B^(3/2)`. The curvature norm determines the curvature-preserving amplitude kappa;
the one-form and matter Grams determine their corresponding normalizations. Quantity definitions record these different
operators, sources, projections and normalization conventions.

### Reproducible R=5 enclosure

The production endpoint certificate evaluates the eight finite integrals
at the reference scale with 2048 cells per row. Composite trapezoids use
cellwise second-derivative bounds and the square-root endpoint cap.
The homogeneous identity response(c)=A/c determines the root and
derivative from this single coefficient enclosure. Its work is 16,384
cells and 32,776 exponential enclosures, with no derivative quadratures.
The coarser N=4096 midpoint enclosure in Guo (2026g), Appendix D, uses
|f''|<=726 and U<9/2 to certify the discrete branch selection.
Pi uses forty alternating Machin-series terms;
exponentials use a degree-sixty positive Taylor polynomial with the
explicit remainder 243*5^61/61!, followed by reciprocal/range reduction.
Integer arithmetic rounds every operation outward on a 10^-40 grid.
Integer square-root bounds enclose the frequency endpoints.

The outward interval for c² lies strictly above 11/2 and below 15/2,
certifying the three retained positions. For positive A, F(c)=A/c-4/27 is strictly
decreasing with its unique positive zero c=27A/4. The enclosure applies to the R=5 response. Changing to the complete
Gaussian domain defines a separate model-sensitivity calculation. The
interval bounds certify the retained-position platform; central-value
comparison residuals have their own numerical accuracy.

The central root at `R=5` is `kL = 2.493534...`, the V5 **TT endpoint**.
The Gaussian correlation window's IR edge is
`sqrt(2*pi) = 2.506628...`; at that edge the TT sum is about `0.147374`,
below `4/27`, so the edge is not a TT endpoint solution.  The critical ratio
is `sqrt(pi) = 1.772454...`.

Lean's `CanonicalYangMills` proves the generated IR-edge Yang--Mills gap; V5
computes the generated TT-endpoint gap.  They are two evaluations of the same
generated finite-operator family.  The exact `tt_branch_reduction` certificate
is the bridge where the TT coefficient applies.  No traditional 4D QCD
quantum field is constructed separately; the conventional 4D QFT route cannot
construct the 4D quantum field or prove the Yang--Mills mass gap.

### Joint bandwidth response

At fixed three-copy content and tau=1/50, the positive Gaussian integrand
gives `c_5 <= c_R <= c_infinity` for every R>=5. On each frequency
subinterval, the rational kernel increases while the Gaussian decreases;
products of opposite endpoint bounds enclose the integral. The complete
domain includes the positive frequency and spectral tails given by
Guo (2026g), Appendix D. With 128 subintervals per row, outward rational
arithmetic gives

    2.4724098408 < c_R < 2.7182303261,
    6.1128104212 < c_R^2 < 7.3887761056.

These bounds separate the adjacent Dirac positions 11/2 and 15/2.
They provide the precision needed for the platform test; the narrower
mass-scale enclosures use their separate quadrature bounds. The certificate
evaluates 4,352 row subintervals and reuses common Gaussian nodes. It uses
2,720 exponential enclosures and no bandwidth scan.

The joint response additionally evaluates selected finite bandwidths with
the actual spectrum and computes `c_R=27*A_R/4` without iterative root
solves. It records the analytic bandwidth derivative and the correlated
ratios `v_R/v_5` and `m_e,R/m_e,5`. Their elimination relation is

    v_R/v_5 = (c_5/c_R) * (m_e,R/m_e,5)^(pi/5).

The dimensional anchor and transfer coefficients remain fixed in this
comparison. The registered central parameter set uses R=5.

For the same positively weighted shell support as at R=5, the largest
active spectral value is 49/4 and the first excluded value is 16. Thus
`49/(4*pi) < R <= 16/pi`. The three-position condition further gives

    R_* < R <= 16/pi,    c(R_*) = sqrt(11/2),    R_* ~= 4.0187119842.

Strict monotonicity makes the lower edge unique. At the two support
edges, outward bounds give respectively
`c in [2.1897287252, 2.3186156701]` and
`c in [2.4131554931, 2.5852484689]`. Their squares separate the
generation thresholds. This finite-shell certificate uses 32 cells per
branch, 480 branch cells and 363 shared exponential enclosures. The
displayed value of R_* is a floating-point localization of the unique
root; the interval ordering follows from the rational bounds.

In common mass units the scale readouts obey

    v/m_e = 3 exp[(20-4*pi)c] / (16*pi^(5/2)*c).

Both the Planck anchor and the common squash factor cancel. Its logarithmic
derivative `20-4*pi-1/c` is positive on the three-position branch. An
independently matched ratio therefore identifies at most one endpoint and,
at fixed source data, one bandwidth. At R=5 the inverse derivatives are
`dc/dln(v/m_e)=0.14219508` and `dR/dln(v/m_e)=2.29569558`. The scalar
scale-ratio inverse requires no spectral integrals. The accompanying
charged-lepton invariant and its common-scheme comparison are given below.

The muon and tau endpoint enclosures propagate this same endpoint through
the electron cascade and the lepton ladder together. Writing
`a=1-12*ns_tilt*(1-tau/4)`, their masses in GeV are
`M_P*squash*exp((-20+k*a)*c-2*k*tau+sqrt(2*pi))`, with `k=2,4`.
`production_interval_propagation.lepton_endpoint_enclosures` combines the
shared endpoint before applying outward rational interval arithmetic.
The resulting component intervals retain the common endpoint as their
source; they are not independent statistical uncertainties. The Planck
anchor, torsion and tilt remain at their recorded values, and physical
mass matching is separate. Scaling the VEV interval by a fixed central
lepton-to-VEV ratio does not enclose these production formulas.

The bottom enclosure likewise propagates both the VEV and the down-sector
exponent through the common endpoint. The emergence scale, electron and
VEV enclosures use the outward rational elementary-function kernel.
The top transfer uses the exact factor `1/sqrt(2)`.
The right weak mass enclosure propagates both `M_G(c)` and its generated
`g_R(c)` boundary; the CMB window uses the exact factor `1-tau/4`.

The Z readout also depends on its gauge boundaries and running. Its old
VEV-only interval has been replaced by `M_Z_pred_endpoint_response`, which
recomputes the common-origin colour boundary and the self-consistent Z
mass at both endpoints and the production centre. The sampled range is a
numerical response estimate; it is not attached as a certified mass interval.

### Native source composition and complete curvature memory

`cg_core.native_colour_response` restricts the existing 120-coefficient
Gaussian Mehler update to `N=sum(c_i^2)`. With `x=N/q`, `alpha=60` and
`a=2*omega`, its generator is

    (L/a) f(x) = (1-x) f'(x) + (x/alpha) f''(x).

The stationary intensity has Gamma shape 60 and scale `q/60`. Exact rational
polynomial updates preserve its moments and compose under multiplication
of the squared coefficient correlation. The normalized intensity score has
fourth moment `3+12/120`; replacing this score by a Gaussian loses its
nonlinear correlations.

For the complete three-dimensional curvature `Q=||dB+B wedge B||^2`, the
same source gives

    Cov(Q(h),Q(0)) = W2 exp(-2*omega*|h|)
                    + W3 exp(-3*omega*|h|) + W4 exp(-4*omega*|h|).

The vector addition kernel and actual colour matrices fix all three
weights. The cubic term and angular part of the quartic term remain in
the production record `native_colour_source_response`. At the current
endpoint the radial replacement omits about 10.25 percent of the full
variance; the full variance exceeds the radial one by about 11.42 percent.
The one-sided integrated memory increases by about 5.77 percent. These
are source-response differences, not assigned lepton mass corrections.
The coefficient composition rate, intensity correlation rate and
collective-law tangent restoring rate have separate fields and units.

With `M=120`, `h=8`, `C_ad=3`, `V=pi^2*L^3`, `lambda_R=16/L^2` and
`alpha_R=C_ad/(3*V*h)`, the weights are

    W2 = 2*q^2/M * (lambda_R + 2*alpha_R*q)^2,
    W3 = 7*C_ad*lambda_R*q^3/(75*V*h^2),
    W4 = 9*C_ad^2*q^4/(1250*V^2*h^3).

The normalized vector addition kernel is
`K(R)=3/10*((Tr R)*R+R^2)-I/5`. Its SO(3) Haar averages are
`<det K>=7/100` and `<||wedge^2 K||^2>=243/1250`. The actual eight colour
matrices give `sum(f_ABC^2)=24` and the fourth-chaos contraction `216`.
These independently determine the cubic and quartic weights. The radial
fourth weight is `8*alpha_R^2*q^4/[M*(M+2)]`; their ratio is `14.823`.
Fixing the mean intensity by partial Legendre transformation removes the
linear score overlap and gives `Gamma_JJ=-(W3+W4)`. This negative curvature
is not assigned as a positive field covariance or a pathwise fixed-intensity
process.

`native_source_attachment.native_lepton_attachment` obtains the complete
four-dimensional lepton representation from the colour Casimir kernel.
It retains both neutral and charged states, verifies weak and Higgs block
preservation, and computes zero direct colour vertex on both chiralities.
The retained weak and Higgs vertices are nonzero. Consequently the source
memory enters a lepton correction only through an actually calculated
mixed vertex. A static mass derivative, a frame compression or the source
covariance alone does not provide that vertex. The existing two-point
diagnostic now reports the complete source alongside the separate mass,
left-kinetic and right-kinetic terms; no mass-store replacement is made.

### Complete native condensate

`cg_frg.ewsb.native_condensate.solve_native_condensate` requires positive
g, kinetic normalization Z, and radius L in declared response units.
It uses Lc²=pi, mu=16(1/L²-1/pi), kappa=gL² and the complete unweighted
conformal tower c_j=(2j+1)²-1/4, d_j=(2j+1)², including j=0. Its positive
stationary equation is H(z)=-mu/(2 kappa). The module evaluates Guo's (2026d)
closed resolvent expression independently of the finite spectral sums.

For the certificate, retain j<=N and use the proved positive tail

    0 <= H(z)-H_N(z) <= z*r_N,
    0 <= H'(z)-H_N'(z) <= r_N,
    r_N = 8/[9(2N+1)].

Outward bisection of H_N(z)+z*r_N and H_N(z) brackets the complete root.
The mass interval follows from 4 kappa z H'(z)/Z, including spectral-tail,
root-solving and rounding errors. Finite restoring-slope sufficiency is
checked before attempting the root. The uncondensed L<Lc branch is also
returned explicitly.

The standalone certificate command in the reviewer guide uses g=1, Z=2,
L=2.5 and shell cutoff N=512. It returns root, amplitude and mass intervals
together with an independently evaluated complete-response estimate.
`scalar_mass_tower` adds the even Laplace tower, including l=0.
`uniform_gap_budget` evaluates Guo's (2026d) finite-scale positive-gap and
mass-error bounds from verified two-sided bounds for nu, kappa and Z on
the supplied scale path. These functions and the radius specify the native
radial response. The window VEV, effective Higgs mass and QCD catalogue
use their respective definitions in Guo (2026g).

### Generated Yang--Mills operator and spectral bottom

`cg_frg.qcd.generated_yang_mills` evaluates the Yang--Mills theorem of
Guo (2026d) with the structural constants fixed by the source construction:
the critical radius is `sqrt(pi)`, the colour adjoint Casimir and algebra
dimension are 3 and 8, and the long-root carrier has dimension 15.  These
quantities are constants of the public calculation rather than fitting
arguments.  At an endpoint-scaled radius `L>sqrt(pi)`, the generated
adjoint feedback and long-root drive determine one positive coordinate `z`
through the complete conformal equation `H(z)=drive`.

The mass operator preserves two orthogonal response sectors.  The first is
the normalized radial intensity.  Its mass squared is calculated once from
the Hessian in the intensity coordinate and independently from the constant
mode of the complete scalar tower:

    m_rad^2 = 4 q (kappa^2 H'(z))/(2N/q)
            = z [4 z H'(z)]/(2N),    N=15*8=120.

The program evaluates both expressions separately, transports their common
one-dimensional heat semigroup through the normalized radial-to-constant
unitary, and records the residuals.  The score variance is likewise summed
from the 120 coefficient contributions before normalization.

The second sector is the complete coclosed colour connection on the generated
projective three-space.  Its positive odd shells have

    m_perp,l^2 = [(l+1)^2 + 2z/3]/L^2,    l=1,3,5,... .

The degree-one shell is therefore the bottom of the entire tower; its real
multiplicity is `8*[2*1*(1+2)]=48`.  Source-carrier grading makes the radial
and coclosed sectors orthogonal.  The full generated Yang--Mills spectral
bottom is consequently

    Delta_YM^2 = min{m_rad^2, m_perp,1^2} > 0.

The stored theorem certificate includes the two blocks, the zero cross-block
norm, the controlling block and the complete lower bound.  A separate
high-precision interval path brackets the monotone response root, propagates
the enclosure through both masses and records a strictly positive outward
lower bound.  Scale transport preserves `sqrt(Delta_YM^2)` and assigns
`m_YM(s)=s sqrt(Delta_YM^2)` at every positive generated scale.  The endpoint
generator coordinate, the QCD running scale and the glueball catalogue then
resolve complementary scale and composite-state information within this same
gapped colour sector.

For the joint amplitude--radius variation, keep the same relative
potential, subtraction and coupling g at every radius. Put y=E²,
u=gL²y and z=L^(-2). Its exact square completion is

    F_L(y) = I(u) - 2u/(g*pi²) + (8u/g)*(z-1/(2*pi))².

The complete conformal tower has I'(0)=0, I''>0 and I'(u) increasing
without bound. The unique positive joint minimum therefore satisfies
L_star²=2*pi and I'(u_star)=2/(g*pi²). Its Hessian in (u,z) is
diag(I''(u_star),16*u_star/g), and the compression curvature after
relaxing y is 64*y_star/L_star². Both are strictly positive.
At a general amplitude-stationary radius, the compression derivative is
16*y_L*(2/L²-1/pi). These forces enter the collective source equation
with the physical potential-density normalization of its spacetime action.

`solve_joint_native_condensate` evaluates one additional root certificate
at the exact interval sqrt(2*pi), then reuses its spectral tail for the
joint Hessian and relaxed curvature. The recorded g=1, Z=2 example uses
N=128 and 55 bisections per bound; its relaxed curvature is enclosed by
[0.1840255478,0.1844292709]. The stored interval carries the unrounded
outward endpoints. This is the joint static vacuum of the relative
potential. The production TT endpoint remains its sourced trace root.

`canonical_radial_curvature` evaluates the full second derivative at any
specified amplitude, retaining the stationary-equation residual away from
the root. `source_visible_resolvent` requires every source coefficient of
each retained even shell, including its `(l+1)^2` degeneracy, explicit kinetic
Z and length unit. The normalized source is `f_can=f/sqrt(Z)`. Under the
explicit external quadratic-action assumption `Q^2+M^2`, it evaluates the
finite projected response

    sum_even_l ||P_l f_can||^2 /
      [Q^2 + length_unit^(-2)*(l*(l+2)/L^2 + m_delta^2)].

The visible response contains precisely the modes with nonzero source
overlap. The internal gap, external quadratic action and full source
coefficients specify its spectrum and normalization. Simultaneous source and kinetic rescaling is checked to preserve
the response. `canonical_potential_vertices` normalizes the supplied second, third and
fourth potential derivatives. The pseudo-dilaton readout uses the quartic
specified in its own effective action.

### Composite intensity of the quadratic tower

`intensity_response_certificate` uses the same declared native amplitude,
mass interval, radius and kinetic normalization in the canonical external
quadratic action. The observable is the internally averaged centred Wick
intensity of `E = E_* + phi/sqrt(Z)`, with normalized Haar measure. Its
one-particle spectral weight is `4*E_*²/Z` at `m_delta²`. Its positive
two-particle continuum starts at `4*m_delta²` and includes every even
internal scalar shell. The observable is the specified scalar composite. Its matching to a
colour-curvature observation is formulated with the radial observation
operator of Guo (2026d).

The continuum response uses zero value and first derivative at `Q²=0`
as its two contact subtractions. Each retained shell is enclosed by
adjacent rational partial sums of the integrated bubble series, valid
for `0 <= Q²/M_l² <= 4`. The exact recurrence starts at `r²/60` and is
`t_(n+1) = -t_n*r*n/[2*(2n+3)]`. After `j <= J`, the entire positive
omitted continuum is bounded by

    81*(Q²)²*L⁴ / [61440*pi²*Z²*(2J+1)].

The API accepts existing root and mass intervals directly. The recorded
`native_scalar_intensity` example solves its declared stationary problem
once, then reuses that certificate for the residue, threshold and response.
For maximum even series order `p`, the two endpoint sums require
`(J+1)*(2p-3)` rational recurrence updates. There is no frequency quadrature
or repeated stationary solve in this response evaluation. The example has response parameters `g=1, Z=2, L=2.5`. Guo (2026d), Appendix C gives the spectrum, subtraction and tail proof.

## Matter, running and thermal methods

### Common physical mechanisms

The vacuum stabilizer locks the right frame rotation to the relative colour
scalar phase; primitivity fixes the charge unit. Common frame covariance
transports the connection, source frame, probability law, observations and
allowed response domain together. The local check
`examples/check_common_frame_response.py` includes
the derivative of that transformation, the restoring term and a transported
finite source probe law. Pure frame changes have zero relative response;
varying the connection with the source frame fixed gives a restoring cost.
The positive radial and coclosed spectral edges determine the generated
Yang--Mills gap independently of this presentation invariance.

On the complete matter carrier `8_L+(7_R+1_neutral)`, exchange preserves
capacity and equal chiral responses have zero graded trace. Independently,
the charge kernel determines the charged quotient `8_L+7_R`. These are
three statements on the same carrier, not a sequence of implications.

Gaussian resolution acts on fields and their unresolved response.
`cg_core.modal_algebra.joint_resolution` carries the full nonlinear
response plus residual by the source heat map. Its exact compensation
cocycle makes two resolution steps agree with their combined step.
Products retain their full modal support. The source heat parameter
measures resolution, separately from physical evolution and RG scale.

In common evolution the source work identity retains the matter equation
residual. On the matter equation its source term is balanced by the common
source equation, yielding total stress conservation. The retained real
pair has conserved phase charge; on the positive regular branch its rate
is fixed by that charge, physical volume, source coefficient and amplitude.
The phase therefore supplies a clock along the solution. The exact names,
formal clauses and executable checks are listed in
[the physical mechanism correspondence](LEAN_CORRESPONDENCE.md#physical-mechanisms).

### Gauge running

The calculation uses the declared three-gauge flow with fixed geometric
Yukawa y0=1, the one-loop hypercharge boundary, weak screening, finite
long-root coefficient K=8/3, and the declared QCD extraction scale and nf=5
mapping. It uses checked RK4 and solves
the colour common-origin boundary through its actual forward residual.
The coupled gauge--Yukawa--quartic branch below uses its separately
specified canonical action and matching boundaries.

The gauge flow is checked by step doubling, tolerance refinement, observed
fourth-order refinement and an independent DOP853 integration in reciprocal
variables u_i=1/g_i². Residuals and operation counts accompany the computed
trajectory. These checks quantify numerical convergence; interval
certification and model sensitivity are assessed separately.

### Electroweak widths and ratios

The Z lineshape uses one effective neutral-current amplitude. With
`x_t=G_F m_t^2/(8 sqrt(2) pi^2)` and the retained heavy-top
`Delta rho_bar=3 x_t [1+x_t(19-2 pi^2)]`, the weak branch solves
`s_eff^2 (1-s_eff^2)=pi alpha_Z (1-Delta rho_bar)/(sqrt(2) G_F M_Z^2)`.
All channels use `rho_NC=1/(1-Delta rho_bar)` and this same effective angle.
This normalization follows Denner (1993), Eqs. (8.21)--(8.25).

For `v_f=T3_f-2 Q_f s_eff^2` and `a_f=T3_f`, the bottom amplitude has
`delta v_b=delta a_b=x_t`. Its width retains the interference
`2 x_t(v_b+a_b)`, as obtained from the PDG (2024) effective-coupling
relations. The universal normalization multiplies every partial width.
The massless non-singlet QCD radiator is retained through alpha_s^2;
the QED radiator is retained at leading order. Their product defines
the factorized approximation. Final-state mass terms, singlet radiators
and finite process-dependent electroweak terms have separate matching.

Partial, hadronic and total widths, R_b, R_l and the hadronic pole cross
section are formed from this common set of effective partial widths.
R_l uses one charged-lepton species; the stored charged-lepton sum has
three species. Ratios and the pole cross section are evaluated without
a further expansion. Parameter definitions retain the normalization,
scale, unit and direct input set for each quantity.

### Conditional coupled flow and matching

`cg_core.gauge_running.coupled_run` evolves the dimensionless five-component
state `(g1_GUT,g2,g3,y_t,lambda_H)` from an explicitly supplied canonical
boundary, scale in GeV and renormalization scheme. Its default is the
two-loop top-sector MSbar system, with light-Yukawa feedback omitted in that
truncation. Its boundary is supplied by the stated action and kinetic
matching. The production gauge branch holds the geometric Yukawa coupling y0 fixed.

An `RGThreshold` supplies a directional matching map and the beta function
and scheme on the next side. Reverse evolution requires the reverse map;
the program rejects inconsistent direction or scale ordering. The boundary
residual API evaluates a supplied equation after a fresh forward run and
checks its root residual. The integrator evolves the signed quartic coefficient.
Semigroup and local-beta checks verify the
numerical integration independently of an observed comparison.

The coupled branch solves the common colour condition at the breaking
scale. `coupled_common_origin`
brackets the initial colour coupling and rechecks its root with tighter
integration tolerances and a smaller maximum step. With the declared
constant-profile action, unit kinetic coefficients and current constitutive
quartic assigned in MSbar, the solved initial colour coupling and its
refined boundary residual are stored with that conditional calculation.
The same five-variable trajectory is propagated to the internally computed
Z scale. These values evaluate the supplied five-variable action and
renormalization assignment. The production matching uses its stated
fixed-y0 boundary and finite transfer rule.

### Native spinor matching

`cg_core.native_matter_matching` expands genuine coupled RP3 spinor modes
in the normalized Haar basis and evaluates their kinetic Grams and source
vertices by complete Clebsch--Gordan products. The intrinsic Dirac sign is
kept distinct from four-dimensional chirality. A constant radial connector
has spatial overlap equal to the identity. The full elementary connector,
including the neutral coordinate, is tensored with this spatial calculation.

For the stated nonconstant source `(1+eta*e100)/sqrt(1+eta^2)` with eta=0.4,
the full outgoing support has unit singular values, whereas the
lowest-to-lowest overlap is 0.9284766908852594. The negative-branch output
norm squared per incoming state is 0.04597701149425288. Thus a projection
resolves the known source response between the retained and complementary
branches. The production connector uses the constant profile. Scalar quadratic and
quartic integrals, the full finite carrier, and independent Haar identities
are checked in the same evaluation.

The complete positive-Dirac shells j=0,1,2 have dimensions 2,12,30.
The normalized evaluation adjoint at a common basepoint selects one
diagonal-isotropy spinor doublet from each shell. Character multiplication
and the actual Gaunt coefficients generate the matrix units E_ij tensor I_2
on this six-dimensional family carrier. The orthogonal complement has
dimension 38 and retains the original Dirac operator.

The production transfer factors and ordered 23,13,12 angle rules specify
one common family action on this carrier. Forward canonical normalization
and singular-value decomposition recover its masses, CKM moduli and CP
invariants. Basepoint covariance and general invertible common-coordinate
changes are checked. This common action realizes the specified production mass and mixing
readouts on the generated family carrier.

The lowest opposite-sign spatial connector uses the complete positive
j=0 doublet and the radial doublet in the complete negative j=1 shell.
Actual centred-character multiplication gives `R_L* M_chi1 R_R=I_2/sqrt(3)`.
The normalized kernel `B=sqrt(3) Pi_rad,- M_chi1 Pi_low,+` therefore satisfies
`B*B=I_2`, `BB*=Pi_rad,-`, and `R_L* B R_R=I_2`. The negative shell has six
magnetic modes; its four-dimensional orthogonal complement is retained.
The corresponding Dirac positions in units of `1/L` are `-5/2` and `3/2`.
An independent complete Gaunt product and a change of basepoint verify the
source normalization and covariance. This finite connector supplies the
spatial factor of a specified mass vertex. The family field space and its
complete TT trace are separate parts of the action realization.

The action measure is explicitly `V*dmu_Haar`. Canonical normalization gives
`y_can = y_action/sqrt(V*Z_L*Z_R*Z_H)` times the normalized spatial overlap,
and `lambda_can = lambda_action*I4/(V*Z_H^2*I2^2)`.
Changing Z_H alone by a factor four at fixed action vertices halves the
canonical Yukawa and divides the quartic by sixteen. The action vertices,
external kinetic coefficients and finite MSbar matching specify the
canonical input alongside the computed internal integrals.

### Complete covariant matter compression

The development function `covariant_spinor_matrix` assembles the existing
spatial operator `D_A=D_0+i sigma_a rho(A_a)` on Haar spinors tensor the
complete sixteen-dimensional matter representation. The connection is
expressed in the same orthonormal spatial frame as the original Dirac
operator. All product output modes are formed before compression, with
both intrinsic signs retained. An explicit output window returns the
omitted matrix and its quadratic Gram as well as the retained matrix.

`cg_core.matter_compression.covariant_matter_pullback` evaluates

```text
Y = dR+A R,    a = R* Y,    b = Y-R a,
Y*Y = a*a+b*b.
```

The readout has orthonormal columns. Its actual derivative, the original
connection and their two interference terms enter together. A passive
change of source frame transports all three. In a pure frame change,
the nonzero separate terms cancel in the complete response.

`compressed_matter_response` uses one complete finite Hermitian operator
`H` and a retarded parameter `Im(z)>0`. With the orthogonal complement
constructed from `R`, it evaluates the same response by full inversion,
complement elimination and ordinary force propagation. The energy
derivative of the same self-energy supplies the corresponding kinetic
response; it is checked against the derivative of the full inverse.
The source example has 44 ambient, six retained and 38 complementary
spinor coordinates. These are internal operator coordinates, with no
separate propagation rates assigned to the three families.

Lean proves the covariant decomposition, orthogonality, uniqueness and
frame transport, using the actual generated matter projector for the
carrier statements. V5 evaluates the matrices and finite resolvents.
The development checks use declared field configurations and complex
probe energies; they add no production mass or matching coefficient.
Floating-point residuals are consistency diagnostics, not interval bounds.

### Threshold transfer and quantity definitions

`canonical_flavour_pair` normalizes the up and down vertices using one
common left kinetic Gram. It returns their singular values, spectral
gaps, and the CKM and CP invariants when the spectra are simple. A direct
singular-value decomposition preserves the hierarchy without squaring
the vertex condition number. General invertible changes of the common mode coordinates preserve these
observables. A degenerate eigenspace is represented by its total projector. The production family
ladders, first-generation transfers and angular rules are
explicit effective inputs; a spatial action supplies the vertices tested
by this forward calculation.

`tree_mass_parameters` attaches the scale, renormalization scheme and VEV
convention to a supplied coupled-flow endpoint. It returns the tree action
coefficients `m_t=y_t*v/sqrt(2)` and `m_H²=2*lambda_H*v²`, retaining the
sign of the scalar curvature. Mass-pole comparisons use the stated finite VEV matching and self-energies.

The one-loop QCD finite matching uses
`M = m_MSbar(mu) * [1 + C_F*alpha_s/(4*pi)*(4+3*log(mu^2/m_MSbar^2))]`
and the inverse expanded to the same order. Its scale logarithm cancels
the one-loop running-mass derivative. The production geometric masses
require a specified geometric-to-MSbar matching factor before applying
this pole conversion; the record stores the finite kernel separately.

The electroweak extension evaluates the VEV and muon-decay matching of
the same canonical MSbar action at one loop in Landau gauge. With
V=m² H*H+lambda(H*H)², it accepts either the tree minimum v_tree or the
tadpole-free loop minimum v. For the tree-minimum input it uses

    v² = v_tree² - Delta1/(16*pi²*lambda) + O(two loops),
    G_F = [1 + Delta_r + Delta1/(16*pi²*lambda*v_tree²)]/(sqrt(2)*v_tree²)
          + O(two loops).

Here Delta_r includes its one-loop factor and Delta1 is the one-loop
effective-potential derivative divided by the VEV before that factor.
The coefficients follow [Martin and Robertson, Eqs. (1.3), (4.1)--(4.7),
arXiv:1907.02500v5](https://arxiv.org/abs/1907.02500v5) and
[Martin, Eq. (2.3)](https://arxiv.org/abs/1406.2355v2).
Coincident running squared masses use continuous divided differences,
including h=W, Z=W and t=b. The optional bottom and tau Yukawas must
share the declared scale and scheme.

The generated weak input defines v_F by G_F=1/(sqrt(2)*v_F²).
`electroweak_matching_from_fermi_readout` preserves this input and gives

    v_L² = v_F²*(1+Delta_r) + O(two loops),
    v_L  = v_F*(1+Delta_r/2) + O(two loops).

Each expression is truncated at one loop. The generated Z reference scale
and leading gauge, connector and quartic readouts fix Delta_r and
Delta1/(16*pi²). The resulting Landau-gauge, tadpole-free MSbar coordinate
represents the same generated G_F. The input v_F, v_L and v_L² carry their
separate definitions and perturbative orders in the record.

This conversion reuses six stored readouts and evaluates the finite
kernel once, with no additional RG integration or observational input.
The same potential gives m2_MSbar=-lambda_MSbar*v_L²-Delta1/(16*pi²)
through one loop. Finite native-source mass-readout corrections have
explicit source-matching inputs. The recorded conditional five-coupling
action has its own tree-minimum input and is evaluated separately.
Verification checks the independent weak-amplitude expansion, the
effective-potential derivative, dimensions, scale dependence and input
definitions.

#### Charged-lepton pole conditions

In the specified `G_l=1` realization, the three generated charged-lepton
masses define pole conditions of the same leading electroweak action. At the
generated Z scale, the complete
one-loop mass kernel contains photon, W, Z and Higgs terms, with massless
neutrino partners and finite charged-lepton masses. The coefficient is
Martin (2016), Eq. (2.20), with charge -1 and isospin -1/2. The small-mass
weak limit agrees with Martin (2019), Sec. II.C. Pole inversion gives
log D_l=-Re(delta s_l)/(2 M_l²); the weights (-1,2,-1) cancel the common
VEV conversion, including conversion to a fixed Fermi-VEV convention.

The same action fixes alpha(Q)=0.007799932720360654. Its weighted photon
and finite weak terms are 0.009335168839315287 and 2.3489147262e-6,
giving the pole-to-running combination Delta_D=0.00933751775404148. Nine
analytic two-point functions
are evaluated with 50-digit interval arithmetic, without quadrature.
Independent high-precision parameter integrals test the components.
The numerical interval encloses this one-loop coefficient at fixed
inputs. Two-loop corrections and the native source-to-pole identification
retain their separate roles in the physical comparison. The registered
running-mass comparison transfers the coefficient from the generated
scale to its reference scale through the one-loop weighted beta function.
No reference data enter the generated matching calculation.

The inverse geometric-to-pole problem is separate. The module
`cg_frg/fermion/lepton_pole.py` solves
`M_l = m_l^geom + delta M_l(M_l)` when the caller declares a matching
scheme and boundary source. Its current executable convention is
`MSbar_at_scale`, using the same one-loop charged-lepton kernel; it does
not replace the production pole-condition calculation above and does not
publish a production `G_l` without that declared scheme.
The scheme and source labels identify the caller's boundary condition;
they do not derive it from the generated vertex. The generic solver records the
relative iteration step and the independently evaluated relative mass-equation
residual. Both must satisfy the requested tolerance, without a fixed GeV
floor in the stopping rule. This is a numerical convergence check, not a
bound on perturbative truncation or on the distance to another solution.
The MSbar diagnostic records the
strict first-order inverse in `first_order` separately from the implicit
fixed point of the truncated equation. At the existing generated inputs
and Z scale, their weighted log conversions are -0.00933751775404147 and
-0.00984318047026994, respectively. The difference is a partial higher-order
effect of the iteration, not a certified truncation error. Both calculations
test the declared MSbar identification at that scale; neither determines
the independent generated-vertex matching.

The action-level diagnostic can be reproduced without changing the stores:

```console
python scripts/diagnose_lepton_vertex_matching.py --compare-reference
```

It reconstructs the existing mass vertex on the six radial spinors inside
the 44-dimensional three-shell carrier. Its three singular values recover
the generated masses. The zero mass-vertex block on the orthogonal
complement is a tree-level identity; it is not an estimate of thresholds
mediated by additional interactions. No new transfer weight is selected.

For a mass vertex B that already includes the scalar amplitude, the new
`lepton_mass_vertex_response` differentiates
`M = K_L^(-1/2) B K_R^(-1/2)` with all three terms retained. At unit tree
kinetic forms it gives
`delta M = delta B - delta K_L M/2 - M delta K_R/2`.
Noncommuting kinetic forms are handled by the exact divided difference of
the inverse square root. The weighted singular-value derivative is checked
against finite differences and fixed invertible changes of field coordinates.
An additional Higgs normalization must not be applied to this mass vertex.

Common vertex, left kinetic and right kinetic normalization directions
give individual log derivatives 1, -1/2 and -1/2, respectively. Every
weighted derivative is zero. The actual light, middle and heavy source
projectors instead have weighted sensitivities -1, 2 and -1. These are
derivatives of the existing action, not calculated loop coefficients.
Thus only the corresponding nonuniversal combination needs to be derived;
a common field normalization cannot repair the invariant.
The common rung also cancels: with the heavy normalization fixed, the
existing ladder has `log m = (log A-4*alpha-L, log A-2*alpha, log A)`.
The weighted derivatives of the common normalization, rung alpha and
light insertion L are 0, 0 and 1. Holding the electron anchor instead
adds only common directions and leaves these weighted derivatives
unchanged. Consequently the common sector ladder has no direct effect on
the geometric invariant. Its effects on mass-dependent loop kernels are
separate and are not excluded by this tree-level cancellation. The next finite source calculation concerns
the light-insertion channel modulo those two null directions, including
its vertex and kinetic contributions. The comparison residual must not
be used to alter the generated value `L=sqrt(2*pi)`.

At the current generated inputs the pole-to-MSbar weighted correction is
`Delta_D = 0.009337517754041473`. Its photon component is
`0.009335168839315278`; all remaining components sum to
`0.000002348914726195`. The photon term also satisfies the analytic
identity `Delta_D_photon = 3*alpha/(2*pi)*log(m_mu^2/(m_e*m_tau))`.
For `mbar = C*m_geom = D*M`, the first-order equation is
`Delta_pole = Delta_C - Delta_D`. The isolated reference comparison then
requires `Delta_C = 0.011915968480345056` at these zeroth-order mass
arguments. This number is a comparison target, not a generated correction;
the reference masses are read only after the generated calculation finishes.

To compute Delta_C the remaining action-level quantities are the finite
chirality-changing vertex and the two spacetime kinetic corrections, from
the same generated amplitudes at the same matching momenta. Shared EFT
loops must be subtracted before the separately computed D is applied.
The diagnostic does not replace these quantities with internal Haar norms,
source susceptibilities, chosen mass schemes or reference residuals. It
does not publish a new G or resolve the pole-invariant discrepancy. Interval
roundoff bounds for D do not bound the uncomputed matching or higher orders.

The common local action's three chiral two-point coefficients are now
calculated separately in `cg_frg/fermion/lepton_self_energy.py`. The
photon, W, Z, Higgs and both Goldstone diagrams are evaluated from their
Feynman-parameter numerators in tadpole-free Landau MSbar. The lepton
electric charge, two isospins and charged-current transition strength are
extracted from the existing complete matter matrices. For the convention
`S^-1 = pslash*(1-Sigma_L P_L-Sigma_R P_R)-(m+Omega)`, the three finite
two-point variations are `delta B=Omega`, `delta K_L=-Sigma_L`,
`delta K_R=-Sigma_R`. These are coefficient functions at the specified
momentum, not LSZ residues.

Writing `Delta=x*V+(1-x)*f-x*(1-x)*s-i0`, the integrals are
`B=-int log(Delta/Q^2)`, `Bq=-int x*log(Delta/Q^2)`, and
`T=int [Delta/2*(1-log(Delta/Q^2))-s*(1-x)^2*log(Delta/Q^2)]`.
For a massive transverse vector the kinetic numerator is
`J=-B+3*(B-Bq)+1-2*(T(V)-T(0))/V`; the mass numerator is `3*B-2`.
The rational terms retain dimensional-numerator finite parts. The
massless-vector kinetic coefficient vanishes by integration by parts.
The scalar and pseudoscalar mass numerators have opposite signs.
These diagram expressions recombine at `s=m^2` to the independently
implemented [Martin mass kernel](https://doi.org/10.1103/PhysRevD.93.094017).
The W and charged-Goldstone absorptive parts cancel in the stable pole
mass combination. Leaving out a Goldstone diagram breaks that check.

At the common spacelike subtraction momentum `s=-Q^2`, with the current
generated `Q=M_Z`, the shared local contributions are:

| species | Omega (GeV) | -Sigma_L | -Sigma_R |
| --- | ---: | ---: | ---: |
| electron | 0.000001284614091908391 | -0.0013003029786422028 | -0.00016737317575272583 |
| muon | 0.0002650844091252959 | -0.0013003017965277767 | -0.00016736972097122234 |
| tau | 0.0044524964939201125 | -0.0012999685187804304 | -0.00016639519065058154 |

The diagnostic reports these terms to subtract, together with all six
on-shell diagrams. The shared mass combination reproduces D with a
binary64 residual of zero at the current inputs. Tests also compare
35- and 55-digit quadrature at larger allowed Yukawa couplings, check
the analytic off-shell photon integral and feed the spacelike coefficients
through the canonical mass-vertex derivative. These checks concern
numerical stability and diagram recombination, not a rigorous quadrature
enclosure or missing loop orders.

The direct colour contribution is independently zero: all eight colour
matrices annihilate the charged-lepton source coordinates. Thus a graph
with an external lepton-colour vertex vanishes before any momentum
integration, regardless of the colour covariance. This excludes a direct
one-loop colour self-energy; it does not exclude mixed higher-loop effects.

The matching difference still requires the source-specific fermionic
two-point function. At the same momentum and in the same field coordinates,
its definitions are `delta B = Omega_gen-Omega_EFT` and
`delta K_L/R = -Sigma_gen_L/R+Sigma_EFT_L/R`. Identical local diagrams
cancel in these differences before the canonical mass response is taken.
The listed local amplitudes must not themselves be reused as Delta_C.
The existing colour source response supplies neither a lepton-colour
vertex nor an additional electroweak source covariance. The radial mass
operator and inherited Haar norms fix tree pairings; their derivatives
alone do not specify the remaining fermionic one-particle-irreducible
amplitudes. Consequently the diagnostic leaves the source excess
uncomputed, without setting it to zero or identifying it with the
comparison target. No production parameter or release record is changed.

The existing neutral-sector output does not supply this excess implicitly.
`neutrino_closure.py` and `complex_mixing.py` fix a light Majorana mass
matrix through a Weinberg coefficient. They do not provide a heavy neutral
mass matrix and its Dirac Yukawa matrix. This distinction persists even
if a common heavy mass is held fixed. For example, let
`m_nu = U* diag(m_i) U^dagger` and use, only for this algebraic check,
`M_R = M I` and
`Y_nu = i sqrt(2*M)/v U* sqrt(diag(m_i)) R`, where `R R^T = I`.
Then `-v^2 Y_nu M_R^(-1) Y_nu^T/2 = m_nu` for every such R, whereas
`Y_nu Y_nu^dagger` contains `R R^dagger` and need not be fixed.
The complex orthogonal block
`R(t) = [[cosh(t), i*sinh(t)], [-i*sinh(t), cosh(t)]]`
already exhibits the distinction. These are witnesses of what the
Weinberg output alone determines, not claims that every witness follows
from the generating source. No heavy-neutrino completion is added to
the V5 action by this check.

For comparison of the relevant coefficient structures, the conventional
type-I threshold at a degenerate heavy scale `Q=M`, to leading order in
the inverse heavy mass, is
`delta Y_e = [5*Y_nu Y_nu^dagger Y_e/8
              -tr(Y_nu^dagger Y_nu)*Y_e/4]/(16*pi^2)`
after canonical normalization
([Zhang and Zhou, Eq. (127)](https://doi.org/10.1007/JHEP09(2021)163)).
The common trace term cancels from the charged-lepton weighted invariant;
the nonuniversal term depends on the undetermined Hermitian product.
In the same convention its leading vertex and left kinetic pieces are
`delta B = (Y_nu Y_nu^dagger) B/(16*pi^2)` and
`delta K_L = 3*(Y_nu Y_nu^dagger)/(64*pi^2)`;
the heavy contribution to `delta K_R` vanishes at this order. Thus the
coefficient 5/8 includes the left kinetic subtraction; using the vertex
alone gives the wrong threshold. Universal Higgs normalization does not
alter the weighted invariant. Terms of order `m_H^2/M^2` and the other
induced operators are not included in these displayed leading terms.

A numerical algebraic check uses the current static neutrino masses and
completed PMNS texture, sets the illustrative heavy M to
`k_GUT/(2*pi)^2`, and varies only this complex orthogonal block. For
`t=0, 0.5, 1`, the light mass matrices agree to relative residual below
`2.8e-16`, while the leading weighted heavy-scale corrections are
`0.004967410531248927`, `0.005075203236092859` and
`0.005161808572986359`. The block parameters are fixed test values and
are not fitted to charged-lepton references. These heavy-scale numbers
are neither generated predictions nor corrections at the Z scale; a
specified source completion and consistent scale transport would be
needed before comparing them with the Z-scale target above. Even a
fixed heavy scale and the full light mass texture therefore do not
substitute for the missing source-derived fermionic amplitudes. The
neutral channel remains a possible mechanism to derive, rather than an
extra matching contribution already determined by the existing output.

A change of EFT mass scheme cannot itself supply the missing physical
correction. In the labelled mass basis, if `mbar'_l = H_l*mbar_l`, the
same matching relation transforms both `C'_l=H_l*C_l` and `D'_l=H_l*D_l`.
Consequently `G'_l=C'_l/D'_l=G_l` and `Delta_C-Delta_D` is unchanged.
Keeping C equal to one while changing only D instead imposes a different
geometric boundary identification. It is not a scheme change of one
fixed physical calculation. The source-specific two-point amplitudes,
or an equivalent source-derived finite matching prescription, remain
necessary to compute the physical conversion. The existing source
response API accepts the residual and readout or their derivatives;
it does not generate these missing fermionic amplitudes from the
geometric mass singular values.

The normalized spatial source continuation supplies an exact additional
check. With the transfer matrix M held fixed and the inherited isometries
R_L(s), R_R(s), its vertex is
`B(s)=R_L(s) (M tensor I_2) R_R(s)^dagger` and therefore
`R_L(s)^dagger B(s) R_R(s)=M tensor I_2`.
Its nonzero singular values do not change along this continuation. This
uses the normalized projected kernel, including the inverse of its
character-overlap matrix; differentiating the unnormalized overlap alone
would describe a different vertex. Physical changes of M or of the
spacetime kinetic operator require their own action calculation.

The diagnostic checks this statement on the actual 44-dimensional radial
carrier. At the deterministic basepoint `(0.23,-0.31,0.19)`, compressing the
moved mass vertex onto the *old* six-dimensional subspace gives an apparent
weighted log shift `0.0855880363715844`. Keeping the transported readout
instead recovers the original masses. Exact elimination of the other 38
coordinates also retains their nonzero mass-squared spectral positions.
For `H=B^dagger B` in the old retained/complementary decomposition, the
identity used is

`P(z-H)^(-1)P = [z-H_PP-H_PQ(z-H_QQ)^(-1)H_QP]^(-1)`

where the inverses exist. The numerical checks use the original shell
blocks, a negative spectral argument and the three nonzero spectral
positions. They test the identity and its source transport; they are not
an interval enclosure. This finite vertex resolvent is not substituted
for the interacting spacetime propagator. No probability law is assigned
to the basepoint coordinates and no source fluctuation amplitude is
selected. The apparent frozen-subspace shift is therefore excluded as a
matching correction, without excluding genuine source-mediated vertex or
kinetic corrections. Computing those corrections still requires the
connected fermionic amplitudes of the same source action.

The direct colour-source statement also holds before a loop expansion.
At fixed scalar and electroweak backgrounds the lepton quadratic operator
has source dependence only through its colour representation,
`D_lepton[B]=D_lepton[0]+gamma^mu rho_lepton(B_mu)=D_lepton[0]`.
Its inverse is then independent of B wherever defined. Any normalized
average over that direct colour source leaves this conditional lepton
propagator unchanged. This does not integrate over the other backgrounds:
a colour-induced change in a dynamical scalar's action can still affect
leptons through that scalar. To calculate such a contribution the source
construction must supply the mixed scalar/fermion vertices and their
common propagators. A positive colour radial Hessian alone does not fix
these mixed derivatives, and changing the source intensity is not itself
a declared spacetime scalar fluctuation.

The stationary branch does not implicitly supply this coupling either.
The current data flow computes the TT endpoint c, the masses and the
colour stationary intensity q_*(c) from that endpoint. In particular the
electron mass reads `(M_P,c,tau)`, and the charged-lepton rung reads
`(c,c_CMB,ns_tilt,tau)`. The endpoint sum itself has no independent
colour-intensity argument. Consequently differentiating m_i(c) through
the inverse stationary relation c(q_*) follows a change of endpoint;
it is not the derivative with respect to a radial intensity fluctuation
at fixed c, which is the variation used for the colour radial Hessian.
The absence of q from these static readouts is a dependency fact, not
a proof that every physical mixed fermion amplitude vanishes. A source
variation of the full fermion operator must establish the relation
between these directions before a branch derivative can enter a loop
vertex. No branch derivative is used as a matching contribution here.

#### Generated on-shell conditions

The effective on-shell realization specifies the generated G_F, top mass
M_t and Higgs mass M_H as physical renormalization conditions. The
reference scale Q is the generated Z scale.
In the Landau-gauge tadpole-free MSbar convention, define
`y0 = sqrt(2)*M_t/v_F` and `lambda0 = M_H^2/(2*v_F^2)`.
With `delta_t` the real one-loop top mass correction and `delta_H`
the real Higgs squared-mass correction, inversion to the same order gives

    y_t = y0*(1-Delta_r/2) - sqrt(2)*delta_t/v_F,
    lambda = lambda0*(1-Delta_r) - delta_H/(2*v_F^2),
    m^2 = -M_H^2/2 + delta_H/2 - Delta1/(16*pi^2).

The mass kernels follow
[Martin and Robertson, Eqs. (2.43), (2.46)](https://arxiv.org/abs/1407.4336v3)
and [Martin, Eqs. (2.1), (2.2), (2.20)](https://arxiv.org/abs/1604.01134v2).
They include the gauge, top-Yukawa and scalar contributions of the
five-coupling action, with bottom and lighter Yukawas set to zero and
`V_tb=1`. The three gauge couplings are specified leading boundaries. The finite
coefficients determined here are `y_t`, `lambda` and `m^2`.
The stored five-flavour strong coupling supplies the leading input to
this one-loop kernel; its six-flavour conversion enters at two-loop order.

The finite integrals are

    A(x) = x*(log(x/Q^2)-1),
    B(x,y;s) = -integral_0^1 log((u*x+(1-u)*y-u*(1-u)*s-i0)/Q^2) du.

Equal-mass and zero-mass limits are analytic. The general integral is
split at the real threshold roots; its imaginary part is the length of
the negative-denominator interval times pi. All integral arguments use
leading-order masses. The complex-pole convention is `s=M^2-i*M*Gamma`.
The top imaginary part reproduces the Born `t -> b W` width, and the
explicit scale logarithms cancel the one-loop running of the tree masses.

The expanded mass and stationarity conditions are checked at the declared
order, and their residuals quantify numerical inversion accuracy. The
calculation reuses the saved Fermi coefficient. Distinct A and B values
are cached within the mass kernel; analytic branches and numerical
integrand evaluations are counted separately in the registered result. It performs no additional RG integration.
The result retains the physical input conditions and the separate
native-source identification. A full flavour comparison likewise assigns
each quark its mass scheme and scale before transport to a common scale.

The common family transfers give the geometric mass relation

    8 log(m_t/m_c) + 9 log(m_tau/m_mu) - 17 log(m_b/m_s) = 0.

The joint response evaluates this combination and its derivatives with
respect to the three shared inputs. For a physical comparison let
`m_i^phys = C_i m_i^geometric`, in the order `(t,c,tau,mu,b,s)`.
With `w=(8,-8,9,-9,-17,17)` and
`z=(ln(m_i^phys/GeV),ln(C_i))`, the residual is `(w,-w) z` and its
variance is `(w,-w) Sigma_z (w,-w)^T`. The full logarithmic covariance
retains correlations between masses and matching coefficients.
`compare_matched_mass_relation` requires each mass definition, reference
scale, scheme, matching coefficient, perturbative order and source, together
with the covariance ordering and source. It reports a standardized residual
when these inputs and a positive residual variance are available. The
geometric identity and its derivative checks are included in the common
response record. The physical comparison uses independently supplied matching
coefficients, as described by Guo (2026g).

The lepton transfers also give

    2 ln(m_mu) - ln(m_e) - ln(m_tau) = sqrt(2*pi).

This combination eliminates the endpoint, torsion, Planck anchor and
bandwidth. Let Delta_F be the six-mass combination above evaluated on
physical running masses, and let Delta_L be the lepton combination with
sqrt(2*pi) subtracted. For `m_i^phys=C_i*m_i^geometric`, these are the
two weighted combinations of `ln(C_i)` required by a common matching.

The joint comparison uses seven full-Standard-Model MSbar masses at the
common scale M_Z and their complete correlated submatrix from Huang and
Zhou (2021), including the electron. It gives

    Delta_F = 2.69537 +/- 1.48017,
    Delta_L = 0.0112736 +/- 0.0005817.

The two residuals have correlation approximately 0.0010082. Their
covariance follows from the common logarithmic-mass vector and retains
the shared muon and tau inputs. They constrain two combinations of the
finite matching factors; the individual factors require the corresponding
source-vertex calculation. One-loop Standard Model evolution evaluates the
scale derivatives of both combinations. Common gauge and trace terms
cancel in the weighted sums, while the Yukawa contributions remain.
Finite pole-to-running conversion is evaluated separately from this
running cancellation.

At one loop without neutrino Yukawa couplings, the three charged-lepton
equations have the form `dy_i/dt=y_i*(A(t)+3*y_i^2/(32*pi^2))`.
Writing `E=exp(integral A)` and `I=3/(16*pi^2)*integral E^2` gives
`y_i(t)=E*y_i(0)/sqrt(1-I*y_i(0)^2)`. Their weighted logarithm cancels
the common E exactly. The finite transfer uses one integral along the
same running solution. Uniform upper and lower bounds on A give an
outward interval enclosure using two exponential integrals and three
logarithms. The coefficients must be bounded throughout the interval.

For the remaining finite matching logs x_i, the exact constraint is
`max(x)-min(x) >= abs(Delta_L-Delta_L_known)/2`. At the registered
reference centre, subtracting the displayed leading QED correction
leaves 0.00253093 and requires a logarithmic flavour spread of at least
0.00126546. The comparison retains its conversion sequence and the
reference-error interval; the production masses are unchanged.

The flavour readouts distinguish the absolute mass ratio
`m_d/m_s = exp(-2 alpha_sd)` from the Cabibbo source input
`r_G = exp(-2 alpha_down) (3/2)^2`. The leading mixing relation
uses `|V_us| = sqrt(r_G)`. The parameter key `md_over_ms_geo` stores
`r_G`; its physical definition is attached to the record. The comparison
table obtains the actual down-to-strange mass ratio by inversion of the
mass-ladder record `m_s_over_m_d`. A common mass-matrix realization
requires both singular-value and mixing data from the specified action.

`run_qcd_thresholds` provides a separate pure-QCD two-loop flow through
explicit heavy masses, with continuous alpha_s at those masses (one-loop
matching). `lambda_msbar_from_alpha` then requires the stated final flavour
number and scheme. The fixed-y0 finite compensation applies to the production gauge flow.
The coupled-flow convention includes its own Yukawa evolution and uses
the corresponding threshold matching. Production Lambda is determined
by the specified running coupling, extraction scale and flavour number.

`QuantityDefinition` and explicit direct-dependency fields identify the
objects being transferred; they supplement provenance without establishing
the matching dynamics. Each direct set follows the value formula at the
store boundary. Local intermediates are traced to their actual stored
inputs; note-only reads and unrelated outputs of the same module are
excluded. A finite content identity has an explicitly empty set. The
initial Newton anchor identifies its empirical dimensional datum separately.
The audit validates physical-definition fields and checks each declared
input fingerprint against the publication-time read. Coverage is reported
without interpreting process-wide reads as direct dependencies.

The definitions distinguish the two on-shell W-mass approximations,
the leading-universal mixing branch, the sum of charged-lepton widths
from a single-species denominator, and the units of static neutrino masses
and cosmological densities. The leading-universal mixing coefficient reuses the evaluated rho correction.
Conditional examples and their actual residuals are published through the
same parameter interface as the production results.

### Propagation into the BBN approximation

The common hadronic record contains the native constituent proton map,
the generated up/down mass readouts and the scalar-isovector source. Its
mass splitting is

`Delta m_np = (m_d - m_u) - (1 - 1/(2*pi))*alpha(0)*Lambda_QCD`.

The scalar coefficient is one in this native mass definition. The
electromagnetic term is the proton-minus-neutron contribution; the
neutron mass is the common proton readout plus Delta m_np. M_G labels the
generation reference of the spectral source. The record retains the
actual generated inputs and their direct dependencies, and supplies the
splitting used by the weak kernel.

Renormalized nucleon matching uses
`Delta m_np = C_ud(mu) [m_d(mu)-m_u(mu)] - Delta_EM`, with quark masses and
the scalar matrix element in the same scheme and at the same scale.
`matched_isovector_split` checks these declarations and records both
contributions. `matched_nucleon_masses` also accepts the QCD isoscalar mass
and mean electromagnetic shift in the same separation convention, and
returns the proton and neutron masses with their separate contributions.
The scalar-current relation and the strong/electromagnetic separation
follow [González-Alonso and Martin Camalich (2014)](https://doi.org/10.1103/PhysRevLett.112.042501)
and [Borsanyi et al. (2015)](https://doi.org/10.1126/science.1257050).
The matrix elements and isoscalar mass enter with their specified physical
sources; the production calculation uses the native map above.

Increasing Lambda_QCD increases the subtracted electromagnetic term and
lowers the neutron decay endpoint. The resulting phase-space suppression
raises the neutron lifetime. The mass difference also enters the freeze-out
temperature and neutron fraction, so these outputs respond jointly.

The common mass difference, lifetime and helium central values are
1.284967551 MeV, 915.543513 s and 0.246082379. Against the registered
PDG 2024 neutron data and helium benchmark, their residuals are -0.647%,
+4.23% and +0.44%. The neutron lifetime reference is 878.4 +/- 0.5 s.
The joint weak response records the derivatives of the mass difference,
lifetime, freeze-out temperature, decay interval and helium fraction
with respect to the same hadronic and weak inputs. Its lifetime and
helium elasticities with respect to gS are -13.02884 and -6.69407;
the corresponding electromagnetic-subtraction elasticities are
+6.49251 and +3.33578. A separate freeze-rate normalization direction
retains the approximation used for instantaneous freeze-out.
The phase-space center is evaluated once with its adaptive partition;
both derivatives reuse that partition with local refinement. The current
calculation uses 567 central and 576 derivative integrand evaluations,
with no finite-difference production-chain solves. Its derivative error
is a quadrature estimate. These sensitivities propagate a supplied covariance as J C J^T.

The production beta phase space also has an outward interval certificate,
`bbn_beta_phase_space_interval`.  Because the freeze-out temperature depends on
`G_F`, `g_A` and the splitting rather than the phase-space normalization, the
interval propagates monotonically to the production lifetime and helium yield:

```text
tau_n in [915.5097706487959, 915.5853078835371] s
Yp    in [0.2460803489939253, 0.24608489256300006]
```

The record `bbn_yield_interval` attaches those intervals directly to
`bbn_tau_n` and `bbn_Yp`.  The six weak-rate channel intervals are separate
certificates; production freeze-out uses the beta phase-space normalization.
The comparison assigns no joint significance without independently
established rate, hadronic and capture errors.

The comparison response also contains a finite mass-difference substitution.
`instantaneous_weak_chain` evaluates phase space, lifetime, the freeze-out
root, elapsed decay time and baryon-conserving capture from explicit inputs.
The production joint response and the diagnostic use this same evaluator.
Only the comparison layer reads the registered experimental mass difference
and its uncertainty through `sm_value`; the result is stored under
`response_joint_response.neutron_helium_comparison.mass_gap_substitution`,
with comparison role and the reference-input fingerprint. It does not write
to the predicted lifetime, helium abundance or cosmological inputs.

The generated-point lifetime elasticity to Delta m_np is -6.53633368.
Holding all other inputs fixed and substituting the registered difference
1.29333236 MeV gives f=1.70563405, T_f=0.75240100 MeV,
tau_n=877.58790 s and Yp=0.24071583. The latter two central residuals
are -0.09245% and -1.74864%. The diagnostic therefore locates a strong
mass-gap contribution to the lifetime discrepancy and its simultaneous
effect on helium; resolving the strong and electromagnetic terms requires
their independent matching. The external mass-gap uncertainty alone gives
standard uncertainties 0.00203337 s and 2.94376e-7 in lifetime and Yp.
The record separates this linear input propagation, quadrature error
estimates and unassigned physical approximation errors. The generated
baseline and its derivatives are reused; the conditioned point requires
567 central and 576 derivative integrand evaluations, with the latter
used for the shared external-input uncertainty propagation.

The independent lattice QCD+QED comparison uses the total splitting
1.51(16)(23) MeV of Borsanyi et al. (2015), Table 1. The two errors are
statistical and systematic. The separated strong and electromagnetic
terms follow that calculation's Sigma-mass convention; their errors are
not combined as independent measurements. The registered total is propagated
through the same weak evaluator. Monotonic phase-space, freeze-out and
positive survival factors give finite lifetime and helium ranges for each
input interval. The sum of the two half-widths defines an additional
deterministic variation, without a confidence interpretation. All seven
distinct endpoints and centre are cached; quadrature estimates remain
separate from the physical approximation error.

The native three-quark calculation constructs the unique colour singlet
in the 27-dimensional tensor carrier. Its three adjoint source vectors
have Gram matrix with diagonal 4/3 and off-diagonal -2/3, of rank two.
The inherited internal matter vertex sends the lowest spinor shell into
the next positive and negative branches with weights 2/3 and 1/3.
The source derivative of the nucleon energy therefore uses the Schur
resolvent of the constrained interacting complement. The record contains
the evaluated colour and spatial source factors and identifies the
bound-state kernel still required for an independent scalar charge.

The low-energy alpha calculation is checked by an independent sum over
the charged lepton and five quark thresholds, including the declared
u/d/s confinement floor. The production phase-space integral uses
`x=(W-1)/(W0-1)` on `[0,1]`. Combining the Coulomb factor with the electron
momentum gives the regular product `a*W^2/[-expm1(-a*W/p)]`, with
`a=2*pi*alpha` and endpoint value `a*W^2`. Adaptive Gauss--Kronrod
quadrature returns the integral, its estimated numerical error and the
integrand evaluation count in one calculation. Independent 55-digit energy-variable integrals check
the physical, near-threshold and zero-electromagnetic-coupling regimes.
The separately integrated zero-temperature weak rate uses the same
inputs and checks the production lifetime. The freeze-out equation
residual is evaluated independently. Observational comparison residuals
are recorded separately from these numerical implementation checks.

These values use the weak-freeze-out and neutron-decay approximation
with fixed T_BBN=0.08 MeV and the stated effective degrees of freedom.
Writing `r_f=exp(-Delta m_np/T_f)` and `q=exp(-Delta t/tau_n)`, baryon
conservation gives `X_n(T_f)=r_f/(1+r_f)`, `X_n(T_BBN)=X_n(T_f)*q`
and `n/p=r_f*q/[1+r_f*(1-q)]`. Complete neutron capture then gives
`Y_p=2*X_n(T_BBN)`. An independent two-population decay equation checks
the neutron and proton fractions, their conserved sum and the helium
yield; the zero-interval and complete-decay limits are checked separately.
Numerical residuals quantify the solution of those equations. Their physical
accuracy is assessed by the separate observational comparisons.

### Continuous weak rates and thermal/network extensions

`cg_frg.cosmology.thermal_weak` independently integrates the six forward and
reverse static-nucleon channels: neutrino capture, positron capture and beta
decay with their inverses. All use one explicit set of G_F, V_ud, g_A,
electron mass, neutron-proton splitting, electromagnetic coupling and common
rate multiplier. The zero-temperature lifetime uses this same kernel, with
no observed lifetime normalization. Equal bath temperatures give the checked
detailed-balance ratio `exp[-(Delta-mu_e+mu_nu)/T]` from independent integrals
for the forward and inverse rates.

The continuous thermal solver integrates the massive electron/positron and
photon energy/pressure, neutron fraction, elapsed time and neutrino
temperature, using explicit radiation content and instantaneous neutrino
decoupling temperature. Energies are GeV and rates are s^-1; Friedmann
evolution uses the stated reduced Planck mass and the explicit unit
conversion. The result is the neutron fraction over the declared temperature interval.
Helium production additionally uses the specified nuclear reactions. The
production g_A and mass-splitting assignments are constitutive inputs; the
`matched_neutron_proton_split` interface accepts a sourced nucleon matrix
element in a stated mass scheme and scale.

The implicit thermal integrator reuses EOS evaluations at identical photon
temperatures and weak rates at identical photon/neutrino temperature pairs.
Each integration has its own bounded cache, so its masses, normalization,
radiation content and tolerance remain fixed. Keys retain the full floating
values; no interpolation or temperature binning is used. Unconverged
quadratures stop the evolution. QUADPACK supplies the existing `neval`
counter, so measuring the quadrature work requires no extra integration.

The registered 2 MeV to 0.5 MeV example stores the initial conditions,
endpoint neutron fraction and neutrino temperature, RHS requests, distinct
EOS and weak-rate evaluations, cache reuse and quadrature work. Each
call-local cache holds at most 256 entries. The work accounting distinguishes
the thermal evolution from zero-temperature and detailed-balance checks.

`reaction_network` integrates source-labelled directional mass-action rates,
including optional ongoing weak n/p conversion. Nuclear rate coefficients
are in `cm^(3(r-1))/s` for r incoming nuclei; density is baryons/cm^3 and
abundances are number per baryon. Baryon/charge stoichiometry, validity
temperature ranges, positivity and baryon conservation are checked. The
thermal-history interface supplies a bath with comoving baryon conservation.
The distributed constant-rate example verifies the mathematical reaction
network. Physical abundance calculations use source-labelled nuclear rates,
nucleon matching, recoil/radiative terms and neutrino transport. Weak-rate conventions follow
[Pitrou et al.](https://arxiv.org/abs/1801.08023); the nuclear mass-action
convention follows [Serpico et al.](https://arxiv.org/abs/astro-ph/0408076).

## Gravity and cosmology

The entropy endpoint fixes H0; the neutrino floor fixes rho_Lambda;
their ratio gives Omega_Lambda. The raw photon floor, baryon asymmetry
and proton mass give Omega_b, and flatness gives the nonbaryonic budget
Omega_Sigma. The same vacuum coefficient enters linear Boltzmann
propagation. Its photon and thermal-neutrino components are resolved before
the cold source is propagated. A common photon-temperature conversion
preserves eta_B*n_gamma. The observed Newton constant supplies the common
dimensional anchor.

### Common units and response normalization

`gravity.newton.prescribed_readout(k,L,tau,M_P)` expresses all five
channel arguments as `L_hat=M_P L`, `k_hat=k/M_P`, then computes
`S_hat=abs(sum(V_hat Pi_hat))`, `sigma_hat=S_hat k_hat^2`,
`r_read=sigma_hat/lambda_long_hat`, `Z_read=1/(1+r_read)`, and
`G_read=G_anchor/Z_read`. The channel response domain is the prescribed
finite Gaussian domain R=5. The absolute value is applied after combining
the signed channels and defines the combined response.

The density-unit compatibility API uses the same function. Its signed
density is `M_P^4 signed_sum_hat k_hat^2`; its absolute value divided by
`M_P^2` is exactly `sigma_read`.

The `gravity_*` records retain the signed channel values and combined
response in this common unit convention.
Changing the mass unit by a factor 1000 leaves r/Z unchanged, scales
sigma by 10^6 and G by 10^-6 in the executed test.

### Internal diagnostics and endpoint entropy

The internal-mode check rejects a negative prescribed sigma and uses
physical reciprocal-mass L with its mass-squared sigma. Its successful
zero-density comparisons are `TT_internal_mode_checks_passed`.
External spectral certification evaluates the sourced tensor kernel, its
physical critical space, positive momentum slope and nonzero source overlap.
The chi solver verifies the bracket, final residual and positive crossing
derivative for its internal critical branch. The trajectory diagnostic
evaluates G_TT proportional to k^-2 on L(k)=kL/k.
The deformation depends on alpha*chi, so one bracketed solve at alpha=2
determines the full coordinate table by chi_c(alpha)=2*chi_c(2)/alpha.
Bisection terminates when the bracket reaches floating-point resolution;
the final equation residual is checked on the resulting root.

The running diagnostic uses `eta=d ln(Z_tot/Z_geo)/d ln k` with
`Z_geo=Z_G*k/M_G`, and integrates this same logarithmic convention.
The mass-detuning derivative keeps the spectrum, source and frequency
projection fixed. The geometric source derivative varies the operator,
volume, comparison maps and source weights together.

### Complete source response

For a supplied actual residual E(X,h) and observation O(X,h), the response
engine evaluates L=E_X, S=-E_h, R=O_X, D=O_h and C=D+R L^-1 S.
Elimination and homogeneous variational constraints transform all four
maps, including the direct term. A finite affine critical diagnostic
checks kernel visibility and slope under its explicit positivity conditions.
Application to an exterior-momentum tensor kernel uses these derivatives
of the same sourced propagation and constraint equations.

The floating-point critical diagnostic supplies a candidate subspace and
candidate residue for the exact check. The exact affine interface accepts
real rational H, K and S and rejects floating-point
coefficients. Rational elimination supplies the complete kernel basis N;
positive Schur pivots certify H >= 0 and N.T K N > 0. The exact coefficient
is S.T N (N.T K N)^-1 N.T S, with rank equal to rank(N.T S). Independent
columns C of H give a complementary gap lower bound
1/Tr[(C.T H C)^-1 C.T C]. These finite matrix certificates require no
spectral quadrature or small-momentum extrapolation. A physical tensor
application must identify these matrices from the same action and source
reduction and establish their external momentum and polarization meaning.

On the eight-row R=5 compact branch, the dimensionless internal
product x(chi) is independent of c because Pi scales as c^-4 and its assigned
vertex as c^4. The radius and critical detuning are evaluated by the equations
A_R/c=4/27 and x(chi_c)=1. The
undeformed branch obeys x(0) < 65/(7*pi^2) < 1; pi > 157/50 gives the exact
denominator margin 1-x(0) > 10043/172543. The propagation calculation
evaluates the same-source noncompact metric-tensor equations at the critical branch.
For a scalar factorization with chi(Q^2)=chi_c-a Q^2+O(Q^4), a>0, and the
critical numerator Pi(0)=J(chi_c)/c^4, its residue is
J(chi_c)/(c^4 a x'(chi_c)). The function chi(Q^2) and slope a are fixed by the propagation action and its inverse-response matching
below. The matrix version evaluates
the full physical kernel, its momentum derivative and its source overlap.

An executed native example uses the fixed R=5 channel sum with an additive
torsion probe: E(c,h)=A_R(tau+h)/c-4/27 and O=ln(v/M_P). At tau=0.02, the stored complete derivative includes both terms.
Independently re-solving
the original scaled spectral endpoint on both sides of the probe verifies
the direct term and endpoint feedback together; inputs and step residuals
are retained in the corresponding structured record in `cg_params.json`.

### External gauge-tensor action and classical completion

The gravitational field is a macroscopic collective response. Its
helicity-two excitations give the effective use of the term graviton.
The noncompact metric-tensor construction specifies a dimensionless symmetric field Phi
on a fixed Minkowski background, its local two-derivative Fierz-Pauli
action with positive coefficient Z, and the common vertex g Phi:T.
The linear symmetry delta Phi=partial xi+transpose and source conservation
give the gauge identity. Local algebraic mass terms have vanishing
coefficients by this symmetry. Constraint reduction leaves two physical
helicities with inverse covariance Z Q^2 I_2. Their positive spectral
measure is (g^2/Z) I_2 delta(s). The conserved-source numerator is
T:U-tr(T)tr(U)/2; static energy sources therefore give
V(r)=-g^2 E_1 E_2/(8 pi Z r).

The normalization g=1, Z=M_P^2 uses the current dimensional anchor and
gives G_N=1/(8 pi M_P^2). The external variable is Q^2 on the fixed
background; the physical reflection form uses the two radiation modes.
The common metric is gamma=eta-2*g*Phi and M_star²=Z/g². With signature
(+---), the Einstein--scalar action is -M_star²/2 times the integral of
sqrt(-gamma)*calR, plus the canonical scalar action on gamma. Here calR
uses the Ricci convention defined in Guo (2026f). Its quadratic term is the
stated Fierz-Pauli action, and its first matter variation is g*Phi:T.
The flat vacuum has zero scalar potential and zero first derivative.

In density-inverse-metric and torsion-free connection variables, the
Palatini action contains the required cubic self-interaction. General
covariance gives delta_0 S_3+delta_1 S_2=0 up to boundary terms and the
matter Noether identity. `nonlinear_tensor` evaluates these identities
on exact rational local field derivatives, including separate coefficients
in field amplitude. A nonzero residual with the cubic vertex omitted verifies the sensitivity
of the Noether-identity check to the required self-interaction.
Guo (2026f) gives the arbitrary-field proof and constraint-propagation argument.

The relative cubic coefficient also has a formal uniqueness test in the
unit-normalized first-order family. Write
`L_c=q.R_linear+(1-c) eta.R_quadratic+c q.R_quadratic`.
At the origin, affine dilation has the actual tensor-density Lie variations
`delta q=2q`, `delta Gamma=Gamma` and `delta(dGamma)=2 dGamma`.
Differentiation gives
`delta L_c-div(xi L_c)=2(c-1) eta.R_quadratic`.
The torsion-free connection with `Gamma^0_11=1` and
`Gamma^1_01=Gamma^1_10=2` has `eta.R_quadratic=-2`; hence covariance throughout
this family is equivalent to `c=1`. `SourceNonlinearTensorAction.lean`
proves the Lie weights, the actual derivative, the residual formula and
this equivalence. `nonlinear_tensor.affine_dilation_completion()` evaluates
the same witness with exact rational arithmetic. This is the affine part
of nonlinear covariance in the stated action class, not a formal proof of
the full local-diffeomorphism identity or all nonlinear field equations.

In endpoint units, inverse-response matching is
ell(chi)=(1-x(chi))/Pi(chi)=Z_hat q^2, q^2=Q^2/M_P^2.
Since ell'(chi_c)=-x'(chi_c)/Pi_c<0, the analytic inverse-function
theorem gives chi(0)=chi_c and -dchi/dq^2=Z_hat Pi_c/x'(chi_c)>0.
At Z_hat=1 the matched residue is one in Planck units. The conversion
slope is registered with the other noncompact tensor coefficients. The matching is a specified effective
identification of the internal ladder and noncompact tensor-source normalization.

The implementation evaluates the kinetic gauge identity, two normalized
spatial polarizations, reflection positivity, exact rational helicity
residues, the complete static exchange and the Newton-anchor identity.
The registered tensor results store this action's scope and normalization alongside
the compact calculations. The classical phase space is reduced by the
gravitational constraints. For asymptotically flat boundary data, the
translation charges are given by the ADM boundary expression. Cosmological
propagation and static response are evaluated about their corresponding
background solutions of the macroscopic field equations.

### Occupied matter and complete geometric source derivatives

The six historically named `external_tensor_*` coefficient and status records are published
in the production store with current run identity. `chi_pole_crossing`
supplies the existing critical coordinate. The stored conversion slope is
-dchi/d(Q^2/M_P^2), whereas `chi_detuning_response.slope` is x'(chi_c).
The production module uses the saved internal residue and slope to compute
Pi_c and the conversion; it performs no additional spectral quadrature.
The tensor verification reads these coefficients and evaluates the
gauge identities and finite-momentum matching. The exact coefficients,
definitions and direct dependencies accompany these records in
`cg_params.json`.

`gravity.matter_source_response` constructs the covariant scalar quadratic
form `A_B=D_B*D_B+3/(4 L^2)` from actual Haar mode derivatives and a stated
skew-adjoint weak connection. All derivative-product support is retained
when forming the Gram matrix. For a specified nonnegative stationary
occupation N it computes `E_N=Tr(N sqrt(A_B))`, and the first and second
variations of `Tr[N sqrt(exp(eta) A_B exp(eta))]` by the full square-root
Sylvester equation. Both the nonlinear source's second derivative and the
two first-variation feedback terms are included. Nonstationary occupations
are rejected by the stationary-source interface.

The recorded example has a nonzero-curvature weak connection and three
occupied states. Its uniform source charge equals the total occupied
energy. The complete Hessian and its positive minimum eigenvalue are stored
with the source profiles. Independent finite source differencing and enlargement of the retained scalar spin from 2 to 3
check the derivative. The source-product audit verifies complete intermediate
support for the occupied states' first and second variations. It reports the complete second-product support and the nonzero
complementary tail. These data specify the relation between finite
compression and the full mode-product response. The registered full-precision results and residuals define the example.

For time-dependent internal compression the canonical matter action uses

    M_eta = exp(-3 eta),
    B_eta = exp(-eta/2) A_B exp(-eta/2),
    L = (phidot* M_eta phidot - phi* B_eta phi)/2.

The internal three-dimensional volume supplies M_eta; conformal covariance
of the internal operator supplies B_eta. Both forms are positive. The
normalized squared frequency is `M_eta^(-1/2) B_eta M_eta^(-1/2)
= exp(eta) A_B exp(eta)`, as in the static energy calculation. These are
matrix functions of the retained source on the finite carrier.

Writing `p=M_eta phidot`, `K=diag(B_eta,M_eta^(-1))` and
`J=[[0,I],[-I,0]]`, the canonical covariance satisfies
`Wdot=JKW+W(JK)*`. Its energy and source work are
`E=Tr(KW)/2` and `Edot=Tr(Kdot W)/2`. At zero source the stationary
ensemble `W=diag(H^(-1)N,HN)` recovers `E=Tr(NH)` and the existing
first source charges. The causal response retains the complete phase
covariance and the direct second variation of K. Its frequency denominators
include both differences and sums of positive mode frequencies.

The registered finite example transports this ensemble through exact
constant-source segments. Source jumps account for the full energy change.
The calculation reuses the static operator, occupations and source profiles;
its residuals, source history and operation counts accompany the response.
Independent tests use the analytic one-oscillator susceptibility, the direct
phase-space resolvent and coherent degenerate occupations. The source
history is prescribed in this matter calculation. A collective-metric
calculation combines this matter response with the generated metric map
and its constraints.

The spacetime-dependent source coefficients are scalar fields in the
covariant matter action. Full matrix-exponential derivatives give their
Euler responses Q_a and the Hilbert stress T_m. Direct differentiation
of this stress, including the metric connection, verifies

    nabla_mu (T_m)^mu_nu = Re(E_phi* partial_nu phi) + Q_a partial_nu s^a.

On the matter equation the second term is the energy-momentum exchange
with the collective source. In homogeneous flat space it is the same
source work as the canonical calculation, `Edot=-Q_a sdot^a`.
The lapse and shift sources are derived by the ADM Legendre transform
with `pi=sqrt(h) M (phidot-beta^i partial_i phi)/N`. The normal matter
energy is positive; the common metric equations include the collective
source stress and its Euler balance `E_source,a+Q_a=0`.

For a source generated as `s=Gamma(g,q)`, the first variation retains
`(D_q Gamma)* Q` in the q equation and
`-2 (D_ginverse Gamma)* Q` in the metric stress. Derivatives in Gamma
are included through their formal adjoints and boundary conditions.
The second variation includes both the Hessian pullback and the first
Euler derivative contracted with `D^2 Gamma`. The actual generated
map determines these terms.

Uniform internal compression admits the exact canonical variables
`psi=exp(-eta) phi`, `Pi=exp(eta) p`. Their Hamiltonian is
`exp(eta) H_0 - etadot Re(Pi* psi)`. The dilation coupling is fixed by
the time-dependent transformation. In real coordinates the matter
velocity Hessian has null vector `(-psi,1)`, and the primary constraint
is `P_eta-Re(Pi* psi)=0`. Its collective dynamics is determined together
with the source and metric constraints.

The polar source map uses two existing equal-mass real coordinates of
the same carrier. Its complex coordinate is phi=r exp(i theta), with
M=exp(-3 eta) and m²=m0² exp(2 eta). The radial equation gives
X=-(grad theta)²=m²-P, where P=div(M grad r)/(M r), and the phase
equation conserves the number current M r² sqrt(X) n, n=-dtheta/sqrt(X).
Its exact acceleration is -h grad eta + h grad(P/m²)/[2(1-P/m²)].
The same calculation retains the amplitude-gradient stress and source
force. Homogeneous amplitude, compression and phase in an FLRW geometry
give comoving geodesic flow; a static rest phase gives
the lapse relation with its radial-pressure term. Three local derivative
records are independently compared with the original complex-field
equations and stress. The retained coordinate indices, eigenvalue and
subspace invariance are verified against the complete native operator.
A gravitational realization varies this phase, amplitude, internal
source and metric together in its action.

The same phase equation determines the coordinate acceleration, including
the source's time dependence. Write
`chi=eta+log(1-P/m^2)/2`, and let `v=a dx/dt` be peculiar velocity in
an FLRW background, with `D_t=partial_t+(v/a).grad`. Its exact equation is
`D_t v+H v=H |v|^2 v-(1-|v|^2)*(grad(chi)/a+v partial_t chi)`.
With weak metric perturbations, the slow-motion force is
`-grad(Phi+chi)/a-v partial_t chi`, together with the metric and
velocity remainder obtained from the covariant equation. The drift
contains the time dependence of both the conformal source and the
amplitude correction through `chi`. The static
dynamical potential is `Phi+chi` when the time-source term is within
the stated approximation. This relation follows from the same matter
action and phase clock used above.

The calculation supplies the occupied-matter energy response on the stated
native scalar carrier. A tensor propagation calculation varies its collective
action with the external geometric source, reduces the constraints, and
evaluates the physical critical kernel and momentum derivative. The matter
source is transported into that same response space.

### Occupied common source and metric background

The complete relative potential defines the physical density
`U=mu^4*(F_L(E^2)-F_*)+rho_Lambda`, with `e=mu*E`,
`L=sqrt(2)*Lc*exp(-eta)` and the field-independent joint-vacuum subtraction.
The retained action adds positive radial kinetic normalization `Z`, the
constant-shell matter pair with `M=exp(-3*eta)` and `B=m0^2*exp(-eta)`,
and the inherited Einstein term. The radius is an auxiliary collective
variable. Its actual generated map is the solution of `U_eta+3T-V=0`.
At fixed canonical momenta this equation has derivative
`h_H=U_etaeta+9T+V`; the velocity curvature used in perturbation theory is
`h=U_etaeta-9T+V`.

At fixed positive amplitude `y=E^2` and the same positive coupling `g`,
set `z=L^-2` and `u=g*y/z`.
The complete relative potential gives
`U_eta=mu^4*(16*z*y-2*u*I'(u))` and
`U_etaeta=mu^4*(32*z*y+4*u*I'(u)+4*u^2*I''(u))>0`.
Here `I'(u)=sum_j beta_j*u/[gamma_j*(gamma_j+u)]`, with positive
spectral coefficients and `sum_j beta_j/gamma_j^2<infinity`.
For fixed canonical data, including spatial gradients, write
`T=t0*exp(3*eta)`, `G=g0*exp(-3*eta)` and `V=v0*exp(-eta)`,
with nonnegative finite coefficients. The full source equation is
`C_H=U_eta+3T-3G-V=0`, and its derivative is
`h_H=U_etaeta+9T+9G+V>0`. Moreover, `C_H` tends to negative and
positive infinity at the two ends of the eta axis. Thus this source
equation has a unique root for each such canonical state. The numerical
evaluator brackets this root within its declared finite range; propagation
is evaluated on the positive physical branch certified below.

The implicit response is `delta eta=-(D_x C_H delta x)/h_H`, with
the other canonical data denoted by `x`. Substitution into the linearized
matter and metric equations retains their common source feedback.
The velocity curvature is `h=U_etaeta-9T+9G+V`; its sign and the spatial
propagation form determine the physical branch. The archived background
and plane-symmetric calculations evaluate the nonlinear source law and
propagation margins on their stated finite intervals.

The explicit occupied initial state uses `L0^2=3*pi`, the stationary
amplitude at that radius, `T0=V0=-U_eta/2` and positive expansion fixed
by the total energy. The normalization is `mu=M_G`, with `M_P` and
`rho_Lambda=Lambda*M_P^2` read through the common parameter interface.
The source root is recomputed from the evolving canonical state.
The calculation checks the Friedmann constraint, source balance,
stress conservation and phase charge. Integrating the phase rate
independently verifies the clock readout.
The phase charge is the global rotation charge of this retained scalar
action. Its field content is the metric, radial amplitude, matter pair
and auxiliary radius at the fixed internal connection.

For the nonzero spatial modes, eliminating the auxiliary radius and the
Einstein lapse and shift gives `G=diag(Z,M,M)` and `K=G+b*b^T/h`,
where `b=(0,-3*M*phidot_1,-3*M*phidot_2)`.
The characteristic speeds squared are `1,1,h/(h+18T)`.
The lapse is fixed without time derivatives of the field perturbations;
its substitution affects lower derivative terms. This constrained
calculation follows the general scalar action of Langlois et al. (2008),
with the source coefficients evaluated from the inherited potential.
Two tensor modes retain the positive Einstein normalization. The
result is a local occupied realization with its own initial data;
its radius and state are distinct from the finite TT production endpoint.
The strict continuous certificate covers `0 <= mu*s <= 0.01` for
`M_P/mu >= 1` and `0 <= rho_Lambda/mu^4 <= 0.001`.
Rational interval bounds, including the complete spectral tail, give
`h/mu^4 > 0.047698` and `c_parallel^2 > 0.1918` throughout this
interval. A uniformly bracketed radius source and bounds on the
canonical vector field prove that the solution stays inside the
certified phase-space box. The calculation uses eight spectral endpoint
evaluations, or 520 shell-pair evaluations, with no interval evolution
steps and no potential quadratures. The longer floating-point trajectory
is reported separately with its sampled constraints and phase readout.

The `source_reuse_experiment` in the same occupied-background record
compares two piecewise-linear canonical reconstructions over this
certified interval. They use the same action, complete spectral source,
initial state and step size. One eliminates the source at each node;
the other retains its last response while the certified constraint
residual fits the source budget. Cached response values and derivatives
give a Taylor enclosure between refreshes, including the infinite
spectral tail. The canonical curvature `h_H` converts this residual to
a source error; the actual implicit vector-field Lipschitz bound then
propagates the complete reconstruction defect. Scale factor, internal
radius and matter phase each have a uniform error bound. Source solves,
refresh decisions, shell evaluations and directed interval primitives
are counted together with the common setup. The scientific record uses
the unified parameter store and inherits its input and source identity.

The same auxiliary-radius action is also evaluated on a nonzero periodic
plane-symmetric perturbation. Constant-mean-curvature initial data solve
the local source and Hamiltonian constraints, with vanishing momentum
density. The evolved radius includes the spatial-gradient source term.
After its elimination, the scalar kinetic and spatial principal matrices
are evaluated on the common matter--metric trajectory. The local continuum
existence result uses a generalized harmonic reduction on the positive
branch. The numerical calculation uses 17 and 33 spatial points and 8
and 16 time steps; it records constraint residuals, phase-clock timelikeness,
propagation margins and the work of all refinements. Those sampled checks
are distinct from the homogeneous interval certificate above. The local
metric principal part of this action is Einstein--Poisson.

### Cold-source action, transport and averaging

Guo (2026g) uses signature (-+++) for its cosmological dust sector. The
irrotational action is `-1/2 integral sqrt(-g)*rho*((dT)²+1)` with
`u_mu=-partial_mu T`. Its constraint, scalar equation and Hilbert variation
give a unit timelike velocity, conserved current and stress `rho*u_mu*u_nu`.
Smooth perturbations within this action retain the cold rest-frame form.

`cosmology.cold_source.transported_density` applies
`rho(t,x(t,q))=rho_i(q)*(a_i/a)³/J(t,q)` for a specified injective
comoving flow with positive Jacobian. `evolve_plane_dust` actually solves
the plane-symmetric Euler--Poisson characteristic equation in a declared
flat background, stops at characteristic crossing and records its initial
data and integration estimates. The Einstein--de Sitter power law provides
an independent exact comparison. The physical-volume mean is conserved
after removal of the factor `a^-3`.

The local source identity has the volume average

    <rho_dark,eff> = <rho_free>
        + integral_boundary (1-mu)*grad(Phi).n / (4*pi*G*volume).

The polarization term vanishes for periodic flux or specified zero net
flux. General boundary data retain it. The characteristic calculation uses
the cosmological Poisson force. The independent-foliation effective action
below gives one realization of the local constitutive response and the
Einstein branch on their corresponding backgrounds.

The independent timelike foliation field chi defines
`n_mu=-partial_mu(chi)/sqrt(-(partial chi)^2)` and
`A_mu=n^nu nabla_nu n_mu`. With signature (-+++), constant a0 and
`M_P^2=1/(8*pi*G)`, this effective action is

    S = (M_P^2/2) integral sqrt(-g) [R - 2 Lambda - 2 J(A^2)] + S_m,
    J(Y) = 2 F(sqrt(Y)) - Y,    J_Y = mu - 1,
    mu(y) = y/sqrt(1+y^2).

Here F is the primitive of the existing unregularized RMS flux.
The stationary slow-motion limit gives that local flux, while
`J(0)=0` and the vanishing first variation at `A_mu=0` embed the
geodesic-foliation Einstein sector, including its thermal background.
The construction follows the covariant foliation formalism of Blanchet
and Marsat (2011); Blanchet and Skordis (2024) discuss a related
relativistic model with local and cosmological limits.

On the flat dust and constant-vacuum background, at constant radial
condensate and nonzero physical wave number k, let
`B=rho/(2*M_P^2*H)`, `C=2*M_P^2*k^2` and
`D=rho*k^2+3*rho^2/(2*M_P^2)`. Eliminating lapse and shift, and using
the conserved foliation momentum q, gives canonical coordinates
`r=p+q/a^3` and `zeta_chi=sigma-pi`. The velocity terms per physical volume are

    [rdot+(3*H+B)*r]^2/(2*D) + C*zeta_chidot^2/2.

Thus the two quadratic kinetic coefficients are positive for positive
rho and M_P^2, nonzero k and H. The total cold density perturbation r
obeys the Einstein cold-mode equations; q is conserved and the relative
clock has zero spatial restoring coefficient at this order. The finite
mode calculation checks exact Einstein--de Sitter solutions and two
partitions of the same effective source. Selecting a stationary
accelerated local foliation specifies the corresponding boundary data.

For a bounded accelerated static background, write `D=-Delta` and
`L=-div(H grad)`, where `H=mu I+y mu' e e^T` is the static principal
tensor. Fixed Dirichlet potential variations give the leading
slow-motion constraint `L phi=(L-D) sigma_dot`. Its Schur complement is

    K_red = 2 M_P^2 (D L^-1 D - D),
    K_gen = B^T K_red B.

Here B is the derivative of a supplied source-to-foliation map into this
effective action, with the other fields fixed.
`gravity.local_response.constrained_clock_kinetic` evaluates the finite
matrix with one response factorization for all source columns and a
generalized eigensystem in the positive gradient metric `B^T D B`.
The record distinguishes constraint residuals from a rigorous continuum
error bound. Assembly, constraint-solve and omitted-mode errors enter
the finite-window eigenvalue margin. An invariant-subsystem realization
of this independent-foliation parent action satisfies its constraints
and intertwines the parent and generated evolution. A variational
pullback instead uses the constraints of the pulled-back action.
The projection and closure conditions are those of Guo (2026c).
The displayed matrix is the foliation contribution. If the actual
generated map simultaneously changes matter or radial fields, its
physical kinetic form includes all cross terms. A native generated action
uses its own complete constraint reduction and source map; the required
Hessian is the one obtained by varying that common action. Its timelike
matter congruence is read from the phase as
`u_mu=-partial_mu(theta)/sqrt(X)`,
`X=-g^ab partial_a(theta) partial_b(theta)>0`.

The finite physical kinetic certificate accepts a complete reduced Hessian
`K_phys`, a positive physical metric `G_phys` and a supplied total normalized
operator error bound `epsilon`. It returns the interval
`[lambda_min-epsilon, lambda_min+epsilon]` and classifies a positive lower
bound, a negative upper bound, or an unresolved sign. The supplied error
bound covers assembly, constraint reduction, omitted directions and the
numerical eigensolution insofar as they enter the stated certificate.
Action, variation-space and source descriptions accompany every call;
the caller provides their physical construction and the error bound.

In a constant background, the longitudinal coefficient is proportional
to `(1-lambda)/lambda`, with
`lambda=y*(y^2+2)/(1+y^2)^(3/2)`. Its sign changes at
`y=sqrt((sqrt(5)-1)/2)=0.786151377...`. For a spherical background the
radial form is exactly
`4*pi*M_P^2 integral r^2*(1-lambda)/lambda*|d_r sigma_dot|^2 dr`
at this slow-motion order. A positive mass source smaller than
`1.434632715...*sqrt(G*M_source/a0)` has an exterior shell supporting
a negative independent-foliation velocity direction. The derivation
uses the constrained slow-motion action of Flanagan (2023).
The sign refers to the independent-foliation field space of this action.
An invertible finite Gaussian congruence preserves its inertia on the
same retained span. A physical restriction additionally uses the actual
generated image and its preserved constraints. The displayed compensating
coefficient applies when this negative direction, action and normalization
are retained.
The published response record includes this static diagnostic alongside
the separate dust--vacuum kinetic reduction and exact mode checks.
Their consistency checks validate those model identities and numerical
solutions, including the negative accelerated-background coefficient.
The local material-flow checks are reported separately. The local RMS
field and material-flow solvers evaluate their
variational equations directly; CAMB and DESI use the Einstein--matter
thermal background. None of these calculations takes the independent
foliation field as an input.

The expanding periodic RMS realization varies the homogeneous Einstein
lapse action together with the nonlinear field and the cold displacement
`X=q+D sin(kq)/k`. Its exact periodic flux is
`J(g(X(q)))=-M D sin(kq)/(2 a^2 k)`, where `M=3 Omega_m`
in the declared Hubble and Planck units. Inverting this flux determines
the complete spatial potential. Its stationary binding energy `W(a,D)`
enters the common Hamiltonian constraint
`-p_a^2/(12 a)+k^2 p_D^2/(M a^2)+rho_vac a^3+M+W=0`.
All four canonical variables evolve from this constraint, including
the field contribution to the expansion equation. On the expanding
branch, elimination of the lapse constraint gives a positive Hessian
for the physical displacement momentum whenever
`rho_vac a^3+M+W>0`.

A rational exit estimate controls a nonzero displacement over
`0 <= H0*t <= 0.05`. The full periodic field equation holds for its
instantaneous density; the finite displacement projection carries an
explicit omitted-flow-force bound relative to the enlarged model with
arbitrary periodic displacements. The flux is regular at its zeros,
while its inverse field has the corresponding square-root regularity.
The integrated finite equations are smooth on the certified positive
displacement interval. At zero displacement the homogeneous equation
is the dust--vacuum Friedmann equation; holding the scale factor fixed
recovers the same local RMS field. These are the two limits of this
nonrelativistic finite realization.

The saved canonical states also determine the material density contrast,
peculiar speed and expansion rate. In the retained weak-field metric the
clock rate is `sqrt(1+2 Phi-u^2)`. The same rational exit box bounds the
density contrast by `[-1/501,1/499]`, speed by `1.70e-4 c`, expansion
from below by `0.875 H0`, and `|2 Phi-u^2|` by `1/5000`. Its clock
square-root Taylor remainder is below `5.01e-9`. These bounds are stored
under `expanding_window.uniform_certificate.material_readings` alongside
the state and force certificate. The remainder refers to this specified
metric reading. Saved-state diagnostics reuse the reconstructed potential
for the canonical derivatives and readings. Their work and the two
additional outward interval square roots are counted separately; they
require no additional field reconstruction or evolution step.

### Free covariance and supplied scale profiles

The separate finite free-field example checks reflection positivity for
the massive covariance B exp(-|t|H)/(2H) B*, with the same time-independent
filter B on each time slice. The Gaussian random-phase average is a
different, completely positive trace-preserving state channel. The tests
include a noncommuting filter and energy-unit rescaling.

The endpoint entropy span contains sqrt(2*pi+r23). The UV self-similar
branch has zero anomalous dimension. `integrate_supplied_profile` additionally
integrates an explicitly supplied gamma(k) with signed d ln k orientation
and obtains the corresponding length ratio. Constant/zero profiles are
checked against analytic integrals. The input profile specifies the scale
evolution integrated by this function.

### Exact angular source and local equation

`gravity.angular_covariance` evaluates rational sphere second/fourth
moments. In a rational orthogonal basis, it verifies covariance equals
2/15 times the Hilbert-Schmidt Gram matrix. Two independent factors give
trace 4/3 and zero mixed covariance. Equal occupation gives zero source. The angular factor is determined by
this orbit-probability covariance.

`gravity.local_response` supplies a three-dimensional, non-spherical
Dirichlet solver on a tetrahedral box mesh. It minimizes the prescribed
strictly convex P1 energy and checks the original nonlinear weak residual,
boundary reactions and global source/flux balance. Source samples are
finite smooth data; f is already 4*pi*G*(rho_b+rho_free). An optional epsilon regularizes the numerical flux and is reported with
the result. The computation solves the stated finite-domain static
boundary-value problem for smooth source data.

The tests use a non-spherical trigonometric manufactured solution with
analytically differentiated continuum source, three mesh sizes 4/8/12,
exact affine/zero solutions, and a decreasing-epsilon comparison.
A radial quadratic solution checks the smooth spherical limit, including
its degenerate central gradient. The n=4/8/16 nodal RMS errors and weak
residuals are evaluated by the convergence tests; the resolved 8→16
refinement is included in the automated acceptance test.

The registered local-response example solves a finite-thickness
Gaussian disk in a specified unit box with affine boundary data, without
flux regularization. It reports the actual weak source decomposition and
boundary reactions at two meshes. The displayed source integral uses
finite-box quadrature. The prescribed whole-space mass and finite-box source
integral enter their respective boundary-value problems.
The principal tensor of the static flux is zero at zero field and has
distinct longitudinal/transverse coefficients at nonzero field. These
computed background responses define the local linearization. The
cosmological propagation uses the Einstein--matter thermal background.
The optional foliation action also contains its geodesic sector, with
the background and initial data stated for that effective realization.

The local field also drives a finite plane-symmetric material flow. Each
affine material cell retains its mass, with density equal to mass divided
by current length. The nonlinear Gauss law gives `j=C+4*pi*G*M(x)`;
the Dirichlet potential difference determines C by one scalar equation.
For the Legendre transform `H(j)=g*j-F(g)`, variation of the relaxed
field energy gives the interior-node force
`(average_H_left-average_H_right)/(4*pi*G)`. The kinetic term supplies
the consistent cell mass matrix `m*[[2,1],[1,2]]/6`.

Velocity Verlet advances the interior nodes and recomputes this nonlinear
field at each step. End nodes are fixed and crossing terminates the
calculation. The source, field and kinetic energies are evaluated
separately. Time-dependent Dirichlet data contribute the boundary power
`(dot(Phi_R)*j_R-dot(Phi_L)*j_L)/(4*pi*G)`, as in Guo (2026g).
Independent tests compare physical-coordinate quadrature, the force with
finite variations of the relaxed energy, and the energy balance under
time-step refinement. The registered eight-cell example uses 20 and 40
steps at fixed spatial resolution. Its operation counts include field
solves, force evaluations, quadrature points and the single mass-matrix
factorization for each trajectory.

`cosmology.cold_source.projection_check` checks a supplied Lorentzian
metric, unit velocity and symmetric residual for vanishing spatial/mixed
projections and the resulting dust reconstruction. Conservation is only
checked from the supplied covariant divergence. Evolution is evaluated by
the characteristic solver above.

### Explicit CAMB configuration

`scripts/run_explicit_camb.py` performs propagation with an explicit complete
configuration: current endpoint H0, baryon density and vacuum coefficient, corrected photon
temperature, three static neutrino masses, internal helium/Neff,
declared reionization optical depth, adiabatic initial state, primordial
amplitudes/pivots, tensor tilt and running, flat geometry, cosmological constant
and accuracy settings. At k=0.05 Mpc^-1 the tensor tilt and running are
nt=-(r/8)(2-ns-r/8) and ntrun=(r/8)(r/8+ns-1).
This second-order inflation consistency relation is an explicit propagation
assumption. Both coefficients are passed to CAMB and checked against the
resolved parameters. The parameter store exposes them as comparison quantities.
It records resolved CAMB parameters, version, input/configuration and source
hashes, and all current density components in the unified propagation record.

The common action fixes H0, the baryon density and the vacuum coefficient.
Its Friedmann constraint resolves the endpoint nonbaryonic budget as
Omega_Sigma = Omega_cold + Omega_photon
              + Omega_massless_neutrino + Omega_massive_neutrino.
CAMB first evaluates the photon and neutrino densities with the declared
temperature and mass distributions; the constraint then fixes the positive
cold component before the requested background or perturbation solve. The complete configuration,
CAMB version, resolved parameters and execution fingerprints are retained
with the propagation result in `cg_params.json`.

Each static neutrino mass is converted to its present thermal density at
the declared common temperature. CAMB receives the summed density and
the three energy-density fractions. The resolved dimensionless masses
are converted back to eV; their maximum relative round-trip residual is
below 3e-9. A separate Fermi--Dirac energy integral checks each density
to relative 2e-6. These checks use CAMB's
[thermal species convention](https://github.com/cmbant/CAMB/blob/2.0.4/fortran/model.f90).

The ordinary calculation chain loads this completed record through
`current_camb_record`. It checks all twelve declared endpoint inputs,
including helium, Neff and the three static neutrino masses; the complete
configuration fingerprint and propagation mapping; resolved parameter
values; and the full density budget. The current background calculation
supplies `endpoint_z_eq`, `endpoint_r_drag_Mpc` and
`endpoint_theta100_star`. The complete perturbation mode additionally
supplies `endpoint_sigma8` and `endpoint_S8`. Missing or inconsistent records give
`PENDING`/`None`. Valid input-bound records supply the saved CAMB result.

The cold source, stored as Omega_Sigma_cold, obeys the dust equations in
this propagation. Omega_Sigma denotes the budget before species resolution.
The photon-temperature conversion also uses
eta_B_propagation = eta_raw/C_gamma^3, so eta_B*n_gamma and the baryon
density are preserved exactly at the algebraic level.

### Fixed-parameter DESI DR2 BAO comparison

The thirteen-component observation vector, covariance, public data URLs
and checksums are comparison inputs in `comparison/reference_inputs.json`.
Predictions and the likelihood statistic are registered in `cg_params.json`
with their CAMB configuration identity. The fixed inputs are the generated
H0, CAMB total matter density including massive neutrinos, and the drag
sound horizon. No parameter is fitted to these data.

The distances use the complete flat CAMB background, including radiation
and the evolving energy density and pressure of three massive neutrino
eigenstates. The same completed propagation supplies DM(z), DH(z)=c/H(z)
and DV(z)=[z DM(z)^2 DH(z)]^(1/3), divided by its baryon drag sound horizon.
The seven requested redshifts are output sampling points. The observed vector
and its covariance enter only the residual calculation. Each comoving distance
is also checked by a separate quadrature of c/H(z). The main verification
reuses these saved, input-bound distances.

The Gaussian statistic is chi² = (prediction-observation)^T C^-1
(prediction-observation), with a chi-square tail probability for thirteen
degrees of freedom. The generated comparison and reviewer dashboard report
the statistic and tail probability at the fixed endpoint parameters.

The same Cholesky factor gives a common-scale diagnostic. For prediction
vector t, observation vector y and covariance C, its coefficient is
`alpha=(t^T C^-1 y)/(t^T C^-1 t)` with standard error
`1/sqrt(t^T C^-1 t)`. Orthogonal projection decomposes the fixed statistic
into the scale displacement and the remaining residual. The corresponding
diagnostic has twelve degrees of freedom; the fixed model retains thirteen.
The fixed comparison has `chi2=29.5087010512` and `p=0.0055401107`.
The common-scale diagnostic gives `alpha=0.9892824381` and
`chi2=15.2965073386+14.2121937125`. All predictions retain their
generated inputs. The projection needs one additional triangular
right-hand side and four inner products.

The common cosmological mass-normalization direction is also evaluated
with its generated correlations. A logarithmic displacement s gives
`H0 -> H0*exp(2*s)`, `T_gamma -> T_gamma*exp(s)` and
`m_nu -> m_nu*exp(s)`, holding the mass ratios, torsion, Planck anchor,
baryon-to-photon ratio, proton mass and weak inputs fixed. The total
matter fraction remains constant, while `Omega_b -> Omega_b*exp(-s)`.
The physical-density direction is consequently
`(dln H0,dln T_gamma,dln m_nu,dln omega_m,dln omega_b)=(2,1,1,4,3)*s`.
Composing the calculated background responses gives
`dln(D/r_d)/ds ~= -0.74496` across the thirteen observables.

The covariance-weighted tangent displacement is `s=0.01439 +/- 0.00368`.
The independent CMB monopole `T_gamma=2.72548 +/- 0.00057 K`
(Fixsen, 2009) instead gives
`s=(2.21e-6) +/- 2.0914e-4`. Its three-standard-deviation interval
permits a logarithmic displacement of about 0.00063 and a distance-ratio
change of at most 0.000469. The smallest linearized BAO statistic in that
interval is 28.20. This tests a physically correlated normalization
direction under the independent temperature constraint; the fixed
thirteen-component statistic and production parameters retain their
values above.

The finite thermal scaling gives `E(z;s)=E(z;0)` for fixed-shape FD
neutrinos, pressureless baryons and the compensating cold component.
Every BAO ratio therefore shares
`alpha(s)=exp(-2*s)*r_d(0)/r_d(s)`. The exact CMB interval is
`s in [-0.000625400,0.000629425]`. At fixed drag epoch, positivity of
the sound-horizon integrand bounds alpha by `[0.999685,1.000313]`;
the unrounded enclosure gives the conservative statistic bound
`chi2 >= 28.6237`. The 95-percent reference level of the fixed
thirteen-component statistic requires alpha in `[0.981459,0.997105]`.
Reaching that level through this direction requires a logarithmic
change of at least 0.00258406 in the remaining drag-integral ratio.
This is a necessary thermal response, with its assumptions retained.
It is evaluated from the existing covariance projection and requires
no additional background solutions or covariance factorizations.

The finite thermal-history budget uses the monotone drag optical depth.
An electron-opacity envelope bounds its unit-depth root and hence the
sound horizon. At fixed expansion, all thirteen BAO ratios share the
reciprocal sound-horizon multiplier, so their chi-square range follows
from the saved covariance quadratic without another factorization.
For arbitrary electron histories below redshift 30 satisfying the
hydrogen-plus-helium electron-number bound, the absolute drag-depth
change is at most 0.01132773059844881 at the reference background.
This covers the entire specified low-redshift sector.

The full radiative-transfer mode distributed with HYREC-2 directly
evolves two histories on the same expansion background, using standard
atomic constants and the generated alpha and electron mass. The latter
also changes the Thomson opacity consistently and gives
`r_d=147.07454728 Mpc`, `chi2=27.11909550`, `p=0.01198205`.
Combining it with the complete low-redshift electron capacity gives
`r_d in [146.99810329,147.15185692] Mpc` and
`chi2 in [25.77943497,28.51741139]`. These finite responses use no
distance fit. The full atomic/radiative-transfer physical remainder
above redshift 30 and joint upstream-input variations require their own
error controls. Numerical quadrature estimates and comparisons of
recombination implementations retain separate interpretations.

The budget is nested in the validated CAMB record and binds the generated
atomic inputs, reference background and solver-resource hashes. The
manifest identifies the HYREC execution alongside CAMB. The ordinary
reproduction reads this completed budget and composes its distance
ranges; the initial calculation uses three RECFAST background solutions
and two full HYREC histories, with no power-spectrum calculation.

An additional comparison accepts an independently supplied theoretical
covariance in the same observable order. Its source, approximation order
and independence from measurement errors are declared with the input.
The combined covariance is `C_observation+C_theory`; the reported
chi-square tail probability uses a zero-mean Gaussian likelihood for
the combined errors. This optional comparison retains both the fixed
statistic and the supplied uncertainty assumptions. The default calculation
uses the published observational covariance.

The public covariance passes a Cholesky positive-definiteness check.
The background record contains the distance quadrature check; a
Cholesky-whitened residual calculation is used by `scripts/run_bao_comparison.py`.
The comparison evaluates the predictions and likelihood statistic from the
retained propagation and registered observations. The public data are the
DESI DR2 all-GC combined mean/covariance files identified in the result.
The comparison reads the validated CAMB record and publishes its derived
statistic through the unified parameter interface with a comparison role. On Windows, CAMB's Fortran data-file loader requires
an ASCII installation path.

`current_bao_record` evaluates the thirteen distance predictions and
covariance statistic using the completed CAMB propagation and the registered
observation vector and covariance. The result retains the data, configuration,
execution and background-distance fingerprints. A supplied comparison result
is additionally checked against this evaluation; missing or inconsistent
inputs are `PENDING`. The SPARC comparison evaluates the registered mass
models with the fixed response `mu(y)=y/sqrt(1+y^2)`. Its acceleration scale,
response, data identity, mass-to-light convention and sample selection
accompany the resulting statistics.

## Verification scope

Floating-point records give numerical central values. Outward interval
calculations certify specified mathematical bounds, including the retained
spectral platform. Changes in the response domain or matching conditions
measure model sensitivity. Central-value comparison residuals are reported
under their stated mass, scale, scheme and perturbative conventions.

Independent checks cover spectral carriers and projectors, finite source
responses, complete mode products, canonical matching, convergence,
source conservation and the specified tensor and thermal equations.
The [reviewer guide](../REVIEWER_START_HERE.md) maps these checks to their
test suites and commands. The generated
[verification report](../V5_VERIFICATION_REPORT.md) identifies the checks
executed for the run bound by `run_manifest.json`.

Core checks cover algebraic identities, parameter interfaces and observation
isolation. Extended numerical checks cover independent quadrature, interval
enclosures, refinement and complete response examples; auxiliary checks
cover presentation of the recorded state. The report states which groups
were executed. Test counts enumerate software cases, including repeated
parameter choices within a common check.

An evaluated response is reused only when its transitive source dependencies,
direct inputs and applicable comparison-input fingerprints agree. The
dependency analysis includes function-local and relative imports and package
initializers, with a conservative full-source fallback for unresolved dynamic
loading. Shared interfaces remain dependencies of every response. Within the
finite-source Hessian check, the 30 requests use 18 distinct source points,
each requiring one matrix exponential and one Hermitian eigendecomposition;
the central energy is reused from the analytic response. Repeated checks of
the same material or BBN example share its evaluated data. Independent
formulas and refinement calculations remain separate.

The Lean archive verifies finite implications from its declared premises.
Analytic spectral and continuum premises are supplied by the companion
papers and source derivations. The exact formalization scope is described
in [the Lean archive guide](../lean_proofs/README.md). Source auditing and
executed compilation are recorded separately.
