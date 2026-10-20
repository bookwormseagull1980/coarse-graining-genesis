# Changelog

## 5.0.2 — 2026-10-20

Release run: `20261020T002918Z-eff10097`

### Added

- Full CAMB 2.0.5 production record (`sigma8`, `S8`; `PENDING=0`).
- BBN beta phase-space and six weak-rate outward intervals.
- Production BBN lifetime/yield interval `bbn_yield_interval`, attached to
  `bbn_tau_n` and `bbn_Yp`.
- Attached endpoint-induced intervals for `M_Z_pred`, `m_t_pred`, `m_b_pred`,
  `m_mu_pred`, `m_tau_pred`, `geometric_ewsb_m_WR` and `kL_CMB`.
- Gaussian spectral, trace-kernel and native-potential reference intervals.
- Release facts page and scope/limits page.
- Documentation of the generated Yang--Mills mass gap and of the absence of a
  traditional 4D QCD quantum field construction.

### Changed

- Parameter records: `261`; `DERIVED=260`; `PENDING=0`.
- Full quantity definitions: `261/261`.
- Tests: `708 passed, 5 deselected, 10 subtests`.
- Explicit interval records: `17`; production records with attached interval:
  `9`; centre-only records: `159`.
- Endpoint bracket: `[817081/327680, 3268327/1310720]`, width `2.2888e-6`.
- Version metadata and citation updated to `5.0.2`.

### Verification

All ten release checks pass; see `V5_VERIFICATION_REPORT.md`.
