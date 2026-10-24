# V5 precision budget

Status: release<br>
Version: 5.0.2<br>
Run: `20261024T084548Z-d52375b5`

This document records the numerical enclosures and their propagation in V5.
The canonical release counts are in
[RELEASE_FACTS.md](RELEASE_FACTS.md).

## 1. Certified endpoint interval

The strict endpoint certificate is

```text
kL in [1246766993313/500000000000, 623383657407/250000000000]
   = [2.493533986626, 2.493534629628]
```

with

```text
width            = 6.43002e-7
relative width   = 2.57868e-7  (0.0000258 %)
```

The stored centre is

```text
kL = 2.4935343325226915
```

The centre is a floating-point centre, not the width of the certified
interval.  The certificate proves existence and uniqueness; the remaining
difference between the centre and the interval is a numerical/quadrature
effect, not a 15-digit accuracy claim.

## 2. Propagation to the mass scale and the electron mass

V5 uses

```text
M_G = M_P sqrt(pi) / kL
m_e = M_P exp(-20 kL) (1 - s0 kappa) * 1000
```

At fixed `M_P`:

| quantity | interval from the certified kL | relative width |
|---|---:|---:|
| `M_G` | `[1.731076293789281e18, 1.731076740178032e18]` GeV | 2.57868e-7 |
| `m_e` | `[0.5103512187863545, 0.5103577819656538]` MeV | 1.28601e-5 |
| `v_HIGGS` | `[246.18874796269515, 246.1908007100621]` GeV | 8.33807e-6 |

The electron-mass exponent `20` amplifies the endpoint width by a factor 20.
The current displayed value `m_e = 0.5103542514 MeV` lies inside the
endpoint-induced interval; its last displayed digits are not certified to the
full interval width.

## 3. Coverage of numerical bounds

- `endpoint_S8` and `endpoint_sigma8` are resolved from the full CAMB 2.0.5
  record: `sigma8=0.8123320818`, `S8=0.8322623365`.
- Fourteen `None` aliases (`Omega_Sigma_cold`, `endpoint_z_eq`,
  `endpoint_r_drag_Mpc`, BAO/SPARC/tensor projections, etc.) are lazy
  references that resolve through their `reference` path; they are not
  missing calculations.
- The BBN beta phase-space integral now has an outward interval
  (`bbn_beta_phase_space_interval`, width `1.35e-4`).  The six thermal
  weak-rate channels also have outward intervals
  (`bbn_weak_rate_intervals`), using a finite trapezoid bound plus an
  exponential Fermi-tail bound.  The neutron-fraction ODE still uses
  `solve_ivp` without a validated interval integrator.
- The finite-domain Gaussian spectral channels now have the
  `spectral_channel_intervals` record (trapezoid plus second-derivative
  remainder).  Other spectral integrals still use `scipy.integrate.quad`
  tolerances `1e-14/1e-12` without propagated error bounds.
- All 262 parameter records now have an `error_kind`; the completion pass
  fills the full `QuantityDefinition` schema for diagnostic, structural and
  comparison records without changing their values.
- `M_G`, `m_e` and `v_HIGGS` now also carry endpoint-induced interval records:
  `M_G_interval`, `m_e_interval`, `v_HIGGS_interval`.
- The production BBN records `bbn_tau_n` and `bbn_Yp` now carry the
  beta-phase-space interval directly (`bbn_yield_interval`):
  `tau_n in [915.5097706487959, 915.5853078835371] s`,
  `Yp in [0.2460803489939253, 0.24608489256300006]`.
- Six further production readouts carry attached intervals:
  `m_t_pred`, `m_b_pred`, `m_mu_pred`, `m_tau_pred`,
  `geometric_ewsb_m_WR`, `kL_CMB`. The muon, tau and bottom formulas retain
  their full shared endpoint dependence; the right weak mass includes its
  varying gauge boundary. The Z mass instead has a three-point endpoint
  response with regenerated boundaries and running, not a certified interval.
- 16 explicit interval records exist; 8 production records carry an attached
  interval. 160 numeric records remain centre-only because they are
  multi-input nonlinear, diagnostic bundles or model definitions without a
  single certified input interval.

## 4. Improvement targets

For the electron mass:

| target relative uncertainty | required kL width |
|---|---:|
| 1 % | `5.0e-4` |
| 0.1 % | `5.0e-5` |
| 0.01 % | `5.0e-6` |

The current width `6.43002e-7` meets the 0.01 % target for the electron mass
(`1.28601e-5` relative).

## 5. Certificate construction and work

The exact substitution `u=c*omega` gives `response(c)=A/c`. A single
outward enclosure of the positive coefficient determines the root
`c=27*A/4` and the derivative `-A/c^2`. The certificate uses 2048
trapezoids per row, cellwise second-derivative remainders and an explicit
cap bound for each enclosed square-root endpoint. Its coefficient is
`A in [0.36941244246332044290, 0.36941253772250165936]`.

The eight rows require 16,384 cells and 32,776 exponential enclosures.
Adjacent cells share endpoint values. Root and derivative enclosures use
this same coefficient, with zero additional derivative quadratures.
Production runs load the saved certificate. Source changes require its
regeneration; displaying more centre digits does not refine its bounds.

Mass propagation retains the common endpoint in every closed relation.
Records without a certified input envelope retain their stated
approximation or diagnostic status.

## 6. Covariance and model error

No full covariance is published.  The certified inputs are intervals, not
random variables with a joint probability distribution; a covariance matrix
would require an arbitrary distribution and correlation choice.

No model-approximation envelope is fabricated.  The freeze-out BBN path, the
glueball catalogue and the tree-level EW readout are model definitions.  The
continuous weak-rate extension is a different model path, not an error bar for
the production path.

## 7. Current conclusion

The endpoint bracket is no longer the dominant precision bottleneck at the
0.01 % level: its width is `6.43002e-7` in `kL` and induces `1.28601e-5` in `m_e`.
The displayed decimal digits still do not define the physical interval.

The release has `16` explicit interval records, `8` production records with an
attached interval, and `160` centre-only records. Numeric bars are present
where a certified input interval exists; they are not invented elsewhere.
