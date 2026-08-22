# -*- coding: utf-8 -*-
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

"""Run all isolated cosmology sandbox diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_sandbox.cosmology import a0_evolution  # noqa: E402
from research_sandbox.cosmology import background_diagnostics  # noqa: E402
from research_sandbox.cosmology import ir_cubic_closure  # noqa: E402
from research_sandbox.cosmology.common import bannered_markdown, write_json, write_text  # noqa: E402


def run_all(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    studies = {
        "ir_cubic_closure": ir_cubic_closure.run(),
        "a0_evolution": a0_evolution.run(),
        "background_diagnostics": background_diagnostics.run(),
    }
    write_json(output_dir / "ir_cubic_closure.json", studies["ir_cubic_closure"])
    write_text(output_dir / "IR_CUBIC_CLOSURE.md", ir_cubic_closure.report(studies["ir_cubic_closure"]))
    write_json(output_dir / "a0_evolution.json", studies["a0_evolution"])
    write_text(output_dir / "A0_EVOLUTION.md", a0_evolution.report(studies["a0_evolution"]))
    write_json(output_dir / "background_diagnostics.json", studies["background_diagnostics"])
    write_text(
        output_dir / "BACKGROUND_DIAGNOSTICS.md",
        background_diagnostics.report(studies["background_diagnostics"]),
    )
    index = make_index(studies)
    write_text(output_dir / "README.md", index)
    return studies


def make_index(studies: dict[str, object]) -> str:
    cubic = studies["ir_cubic_closure"]
    a0 = studies["a0_evolution"]
    background = studies["background_diagnostics"]
    assert isinstance(cubic, dict)
    assert isinstance(a0, dict)
    assert isinstance(background, dict)
    derived = background["derived"]
    sigma = background["sigma8_baseline"]
    body = f"""This folder contains generated outputs from the isolated
cosmology research sandbox.

These files are deliberately outside the V4 reproduction chain.  They
read the V4 parameter store as a frozen input snapshot and write only
to this output directory.

## Generated Notes

| note | purpose |
|---|---|
| `IR_CUBIC_CLOSURE.md` | candidate deep-IR nonlinear closure for flat rotation curves |
| `A0_EVOLUTION.md` | frozen vs H(z)-tracking branches for a0 |
| `BACKGROUND_DIAGNOSTICS.md` | standard background, BAO, growth, and rough sigma8 baseline |

## Current Snapshot

| diagnostic | value |
|---|---:|
| a0(today) | {a0["a0_today_m_s2"]:.6e} m/s^2 |
| cubic deep-IR law | v^4 = G M a0 |
| age, standard background | {derived["age_Gyr"]:.6f} Gyr |
| z_eq | {derived["z_eq"]:.3f} |
| z_star | {derived["z_star_Hu_Sugiyama"]:.3f} |
| r_s(z_star) | {derived["r_s_star_Mpc"]:.6f} Mpc |
| sigma8, rough baseline | {sigma["sigma8_rough"]:.6f} |

## Discipline

No result in this folder should be cited as a completed V4 prediction
until the missing dynamics is derived, tested, and promoted into the
formal reproduction chain.
"""
    return bannered_markdown("Cosmology Sandbox Outputs", body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("research_sandbox/cosmology/outputs"))
    args = ap.parse_args()
    studies = run_all(args.output_dir)
    print("cosmology sandbox complete")
    for key in studies:
        print(f"- {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
