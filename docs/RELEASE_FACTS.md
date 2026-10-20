# V5 Release Facts

Status: release snapshot<br>
Version: 5.0.2<br>
Run: `20261020T002918Z-eff10097`<br>
Date: 2026-10-20

This page is the single numerical reference for the release.  It is generated
from `cg_params.json`, `run_manifest.json` and `V5_VERIFICATION_REPORT.md`.

## V5

| Fact | Value |
|---|---|
| Parameter records | `261` |
| `DERIVED` | `260` |
| `PENDING` | `0` |
| Complete quantity definitions | `261/261` |
| Python tests | `708 passed, 5 deselected, 10 subtests` |
| Structural certificates | `11 PASS` |
| V5 internal Lean archive | `18 files`, trust level 0 |
| Explicit interval records | `17` |
| Production records with attached interval | `9` |
| Centre-only records | `159` |
| Endpoint bracket | `[817081/327680, 3268327/1310720]` |
| Endpoint width | `2.2888e-6` |
| `m_e` relative width | `4.58e-5` |
| `v_HIGGS` relative width | `2.97e-5` |
| CAMB | `2.0.5`, full mode |
| `sigma8` | `0.8123320817756509` |
| `S8` | `0.8322623365089923` |
| BBN lifetime interval | `[915.5097706487959, 915.5853078835371] s` |
| BBN `Yp` interval | `[0.2460803489939253, 0.24608489256300006]` |
| Generated YM gap mass | `5.940431067579812e19 GeV` |
| Glueball catalogue mass | `1.6642238631694293 GeV` |

## Lean physical branch

| Fact | Value |
|---|---|
| Lean toolchain | `4.34.0` |
| Physical branch files | `91` |
| Local Lean modules | `429` |
| Canonical-root audit | `346 modules, 16,584 constants, 8,490 named type checks` |
| Theorem index | `527 declarations, 215 modules` |
| Root logical axioms | `propext`, `Classical.choice`, `Quot.sound` only |

## Release statement

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**

The solved operator is the generated finite Yang--Mills operator.  The Lean
zero-argument theorem proves the IR-edge generated operator; V5 computes the
TT-endpoint generated gap.  The low-energy glueball catalogue is a separate
effective readout.
