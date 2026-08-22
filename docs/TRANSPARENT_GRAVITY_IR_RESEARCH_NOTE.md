<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
-->

# Transparent Gravity IR Research Note

This note records a research audit, not a paper edit.  It asks whether
the present V4 linear TT propagator can by itself produce a MOND-like
rotation-curve interpolation function.

## Verdict

Within the present linear TT sector, the answer is no.

Along the V4 self-similar trajectory `L(k) = kL/k`, the TT momentum,
Lichnerowicz shift, and exponential regulator are all proportional to
`k^2`.  Therefore the TT propagator is a massless linear kernel
`G_TT(k) ~ k^-2`.  In three spatial dimensions this gives the ordinary
Newtonian point-source response `phi(r) ~ 1/r`, `a(r) ~ 1/r^2`, and a
rotation curve `v(r) ~ r^-1/2`.

The derived acceleration `a0 = c H0/(2 pi) sqrt(4/3)` is therefore a
real IR scale in the framework, but it is not a dynamics.  It does not,
by itself, produce a nontrivial interpolation function `F(a/a0)`.

## Direct V4 Scan

- scale span: `60.080` decades from `M_G` to `H0`
- `p^2/k^2`: `1.286646617258162`
- max drift in `p^2/k^2`: `4.441e-16`
- denominator/k^2: `2.742600985720038`
- max drift in denominator/k^2: `8.882e-16`
- `slope_G = d ln G_TT / d ln k`: `-1.999999999999999`
- `slope_Z = d ln Z / d ln k`: `-4.11840159418159e-18`
- linear kernel exponent `alpha = -slope_G`: `1.999999999999999`
- acceleration power: `a(r) ~ r^-2.000000`
- circular velocity power: `v(r) ~ r^-0.500000`

## What A Linear Kernel Can Do

For a fixed linear static kernel `K(q) ~ q^-alpha` in three spatial
dimensions:

| Kernel | Potential | Acceleration | Circular velocity |
|---|---:|---:|---:|
| q^-1 | r^-2.0 | r^-3.0 | r^-1.0 |
| q^-2 | r^-1.0 | r^-2.0 | r^-0.5 |
| q^-3 | log(r) | r^-1 | r^0 |
| q^-4 | r^+1.0 | r^+0.0 | r^+0.5 |

Flat rotation curves require the `alpha = 3` row, or an equivalent
nonlinear field equation.  The present TT kernel is the `alpha = 2`
row.

## Scale-Law Scan

The next table tests the toy family `L(q) = kL/q^beta`.  This is not a
new proposal.  It checks whether changing only the self-similar scale
law can generate the missing IR power.

| beta | alpha=-slope_G | slope_G | slope_Z | acceleration power | velocity power |
|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.500097 | -0.500097 | -0.000097 | -3.499903 | -1.249951 |
| 0.50 | 1.000133 | -1.000133 | -0.000133 | -2.999867 | -0.999933 |
| 0.75 | 1.500241 | -1.500241 | -0.000241 | -2.499759 | -0.749879 |
| 1.00 | 2.000000 | -2.000000 | -0.000000 | -2.000000 | -0.500000 |
| 1.25 | 2.003019 | -2.003019 | 0.496981 | -1.996981 | -0.498491 |
| 1.50 | 2.001616 | -2.001616 | 0.998384 | -1.998384 | -0.499192 |
| 2.00 | 2.000879 | -2.000879 | 1.999121 | -1.999121 | -0.499561 |

Result: this family never reaches `alpha = 3`.  For `beta >= 1`, the
regulator term enforces `G ~ q^-2`; for `beta < 1`, the kernel is less
IR-singular than Newtonian.  A scale-law change alone is not enough.

## Nonlinearity Requirement

Deep-MOND point-source scaling is

```text
a(r) = sqrt(G M a0) / r .
```

The source-mass dependence is `sqrt(M)`.  Any fixed linear propagator
has response proportional to `M`.  Therefore a true MOND interpolation
cannot come from the existing linear TT kernel, and cannot come from a
mass-independent linear replacement alone.  It requires at least one of:

- a nonlinear Poisson equation, e.g. `div[mu(|grad phi|/a0) grad phi] = 4 pi G rho`;
- a source-dependent or environment-dependent IR response;
- a new scalar/vector/auxiliary degree of freedom;
- a genuinely nonlocal IR closure with a clearly stated source law.

Each option is a new dynamical closure unless it can be derived from an
existing V4 identity without adding an adjustable function.

## Minimal Nonlinear Candidate

There is one especially clean candidate if the framework chooses to add
an IR dynamical closure openly rather than hiding it inside the linear
TT sector.

Assume only:

- a local quasi-static potential `phi`;
- a second-order Euler-Lagrange equation;
- the existing derived scale `a0`;
- deep-IR scale invariance in three spatial dimensions.

Then the local action density is forced to the cubic gradient form

```text
L_deep ~ |grad phi|^3 / a0 .
```

The corresponding equation is

```text
div(|grad phi| grad phi / a0) = 4 pi G rho .
```

For a point mass this gives

```text
a(r) = sqrt(G M a0) / r,
v^4 = G M a0 .
```

So the deep-MOND branch and the baryonic Tully-Fisher relation follow
from the cubic IR closure.  The uniqueness can be seen from the
general p-Laplacian family:

| p | acceleration power | velocity power | source-mass power | flat rotation |
|---:|---:|---:|---:|---:|
| 2.0 | -2.000000 | -0.500000 | 1.000000 | False |
| 2.5 | -1.333333 | -0.166667 | 0.666667 | False |
| 3.0 | -1.000000 | 0.000000 | 0.500000 | True |
| 3.5 | -0.800000 | 0.100000 | 0.400000 | False |
| 4.0 | -0.666667 | 0.166667 | 0.333333 | False |

In three spatial dimensions, flat rotation selects `p = 3`.  This is
promising because the same number `3` is central to the compact
internal spectrum.  But it is not yet a V4 result.  The transition
function between Newtonian and deep-IR regimes, the relativistic
lensing completion, and the cosmological perturbation equations remain
open.

## Research Boundary

The current framework closes homogeneous background quantities such as
`H0`, `Omega_Lambda`, `Omega_b`, `T_CMB`, `eta_B`, flatness, and the
IR acceleration scale.  It does not yet close the structure sector:
galaxy rotation curves, lensing without particle dark matter,
`P(k)`, `sigma8`, `f sigma8`, BAO, or the full CMB angular spectrum.
