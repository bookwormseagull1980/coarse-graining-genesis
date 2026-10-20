# V5 precision budget

Status: release<br>
Version: 5.0.2<br>
Run: `20261020T002918Z-eff10097`

This note records the current numerical bottleneck in V5.  It is an audit
note, not a new scientific claim.  The canonical release counts are in
[RELEASE_FACTS.md](RELEASE_FACTS.md).

## 1. Certified endpoint interval

The strict endpoint certificate is

```text
kL in [817081/327680, 3268327/1310720]
   = [2.4935333251953127, 2.493535614013672]
```

with

```text
width            = 2.289e-6
relative width   = 9.179e-7  (0.0000918 %)
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
| `M_G` | `[1.7310756104e18, 1.7310771994e18]` GeV | 9.18e-7 |
| `m_e` | `[0.5103411712, 0.5103645333]` MeV | 4.58e-5 |
| `v_HIGGS` | `[246.1856054, 246.1929123]` GeV | 2.97e-5 |

The electron-mass exponent `20` amplifies the endpoint width by a factor 20.
The current displayed value `m_e = 0.5103542514 MeV` lies inside the
endpoint-induced interval; its last displayed digits are not certified to the
full interval width.

## 3. What is actually missing

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
- All 261 parameter records now have an `error_kind`; the completion pass
  fills the full `QuantityDefinition` schema for diagnostic, structural and
  comparison records without changing their values.
- `M_G`, `m_e` and `v_HIGGS` now also carry endpoint-induced interval records:
  `M_G_interval`, `m_e_interval`, `v_HIGGS_interval`.
- The production BBN records `bbn_tau_n` and `bbn_Yp` now carry the
  beta-phase-space interval directly (`bbn_yield_interval`):
  `tau_n in [915.5097706487959, 915.5853078835371] s`,
  `Yp in [0.2460803489939253, 0.24608489256300006]`.
- Seven linear production readouts now carry attached intervals:
  `M_Z_pred`, `m_t_pred`, `m_b_pred`, `m_mu_pred`, `m_tau_pred`,
  `geometric_ewsb_m_WR`, `kL_CMB`.
- 17 explicit interval records exist; 9 production records carry an attached
  interval.  159 numeric records remain centre-only because they are
  multi-input nonlinear, diagnostic bundles or model definitions without a
  single certified input interval.

## 4. Improvement targets

For the electron mass:

| target relative uncertainty | required kL width |
|---|---:|
| 1 % | `5.0e-4` |
| 0.1 % | `5.0e-5` |
| 0.01 % | `5.0e-6` |

The current width `2.289e-6` meets the 0.01 % target for the electron mass
(`4.58e-5` relative).

## 5. Recommended route

1. ~~Replace the first-order cell envelope with a validated higher-order
   quadrature.~~ Done: the composite trapezoid with an outward second-derivative
   remainder tightens the bracket to `2.289e-6`.
2. ~~Use interval contraction below `5e-6`.~~ Done at `cells=2048`.
3. ~~Propagate the resulting `kL` interval through `M_G`, `v_HIGGS` and the
   charged-lepton cascade.~~ Done: `M_G_interval`, `m_e_interval` and
   `v_HIGGS_interval`.
4. ~~Add explicit `error_kind` and interval fields to the remaining high-fanout
   records.~~ Done for the linear production readouts; the remaining 159
   centre-only records need per-record error models.
5. Full CAMB `sigma8/S8` is now embedded from the CAMB 2.0.5 full run.
6. Add a convergence table for `cells`, quadrature tolerances, and the
   resulting interval widths; a stable centre alone is not a certified
   precision claim.

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
0.01 % level: it is now `2.289e-6` in `kL` and induces `4.58e-5` in `m_e`.
The displayed decimal digits still do not define the physical interval.

The release has `17` explicit interval records, `9` production records with an
attached interval, and `159` centre-only records.  Numeric bars are present
where a certified input interval exists; they are not invented elsewhere.
