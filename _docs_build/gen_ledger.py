# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Generate the current V4 ledger from the live parameter store.

The generator reads current artifacts only. Historical notes and merged
development snapshots are deliberately absent from the public ledger.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BUILD = ROOT / "_docs_build"
STORE = ROOT / "cg_params.json"
REPORT = ROOT / "V4_VERIFICATION_REPORT.md"


def load_store() -> dict:
    with STORE.open(encoding="utf-8") as handle:
        return json.load(handle)


def export_params(parameters: dict) -> None:
    target = BUILD / "params_export.json"
    with target.open("w", encoding="utf-8") as handle:
        json.dump(parameters, handle, ensure_ascii=False, indent=2)


def value_text(value: object) -> str:
    if isinstance(value, float):
        return format(value, ".16g")
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def parameter_row(parameters: dict, key: str, meaning: str) -> str:
    record = parameters[key]
    writer = record.get("writer", "")
    return (
        f"| `{key}` | `{value_text(record.get('value'))}` | "
        f"{record.get('provenance', '')} / {record.get('role', '')} | "
        f"`{writer}` | {meaning} |"
    )


def verification_verdict() -> str:
    if not REPORT.exists():
        return "verification report pending"
    text = REPORT.read_text(encoding="utf-8")
    marker = "## Verdict"
    if marker not in text:
        return "verification report present"
    tail = text.split(marker, 1)[1].strip().splitlines()
    return tail[0].strip() if tail else "verification report present"


def build() -> str:
    store = load_store()
    parameters = store["parameters"]
    export_params(parameters)

    provenance = Counter(r.get("provenance", "") for r in parameters.values())
    roles = Counter(r.get("role", "") for r in parameters.values())
    lean_count = len(list((ROOT / "lean_proofs").glob("*.lean")))

    primary = [
        ("G_N_PDG", "single observed dimensional anchor"),
        ("M_P", "reduced Planck mass from `G_N_PDG`"),
        ("tau", "chiral-content invariant `(8-7)/(15*(10/3))=1/50`"),
        ("kL", "spin-2 endpoint fixed point"),
        ("M_G", "emergence scale from the endpoint fixed point"),
        ("lambda_long_MG", "`(2,1)` long-root eigenvalue `16/L^2` at the emergence scale"),
        ("sigma_over_lambda_long_MG", "five-channel self-energy divided by the long-root eigenvalue"),
        ("n_generations", "spectral-capacity map on the even RP3 Dirac tower"),
        ("g2_MG", "screened weak coupling at the emergence scale"),
        ("g1_MG_geo", "squashed-axis hypercharge normalisation"),
        ("g3_MG_geo", "colour boundary coupling"),
        ("v_HIGGS", "electroweak scale from the window-squared line"),
        ("m_e_pred", "electron cascade closure with content exponent 20"),
        ("m_nu3", "Weinberg scale with the squash level factor"),
        ("Delta_m21_sq_osc", "finite-window solar propagation splitting"),
        ("Delta_m31_sq", "atmospheric splitting of the absolute texture"),
        ("qcd_Lambda_QCD", "two-loop colour running and threshold matching"),
    ]

    cosmology = [
        ("H0_GEV", "entropy-endpoint Hubble rate"),
        ("Omega_Lambda", "dark-energy content ratio"),
        ("Omega_b", "raw photon floor, raw baryon asymmetry, and proton mass"),
        ("Omega_Sigma", "flatness endpoint residual"),
        ("T_CMB_corrected_K", "finite endpoint correction of the photon monopole"),
        ("a0_MOND", "endpoint acceleration scale"),
        ("endpoint_acceleration_projection", "normalised local endpoint response"),
        ("endpoint_sigma8", "fixed-input Boltzmann comparison propagation"),
        ("endpoint_S8", "fixed-input Boltzmann comparison propagation"),
    ]
    primary = [(k, m) for k, m in primary if k in parameters]
    cosmology = [(k, m) for k, m in cosmology if k in parameters]

    banner = """<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171

DOI records:
  [Software] 10.5281/zenodo.22067006
  [Paper I]  10.5281/zenodo.22067118
  [Paper II] 10.5281/zenodo.22067469
-->
"""

    lines = [
        banner,
        "# V4 Framework Ledger",
        "",
        "This ledger describes the current formal computation. It is generated from",
        "`cg_params.json`; numerical values below therefore match the latest fresh",
        "reproduction. The two companion papers supply the physical derivations.",
        "",
        "## Records",
        "",
        "- Software: `10.5281/zenodo.22067006`",
        "- Paper I: `10.5281/zenodo.22067118`",
        "- Paper II: `10.5281/zenodo.22067469`",
        "",
        "## Data Discipline",
        "",
        "The computation has four layers:",
        "",
        "1. `OBSERVED / anchor`: the Newton constant sets the dimensional scale.",
        "2. Structural closure: compact RP3 spectrum, content counts, Gaussian",
        "   heat-flow envelope, TT response, endpoint pole normalisation, and",
        "   matching conventions.",
        "3. `DERIVED`: values returned by the acyclic module chain.",
        "4. `comparison`: reference observations and fixed-input propagation",
        "   products evaluated after the internal chain.",
        "",
        f"Current store: {len(parameters)} records; "
        + ", ".join(f"{k}={v}" for k, v in sorted(provenance.items())) + ".",
        "Roles: " + ", ".join(f"{k}={v}" for k, v in sorted(roles.items())) + ".",
        "",
        "## Defining Closures",
        "",
        "- The one-loop TT spectral response is",
        "  `K_TT(k^2,m^2)=k^4/(k^2+m^2)^2`; it satisfies",
        "  `K_TT(k^2,0)=1`. The Ward-normalised subtracted flat amplitude is",
        "  recorded separately.",
        "- With `y=m^2/(k^2+m^2)`, the mass-weighted response is",
        "  `y(1-y)^2`. Its unique interior maximum is `4/27` at `y=1/3`;",
        "  the endpoint closure adopts this extremum as its pole normalisation.",
        "- The torsion modulus is the dimensionless content invariant",
        "  `tau=(N_L-N_R)/(N_f SumY2)=1/50`.",
        "- The generation capacity is the declared map",
        "  `n+3/2 < (kL)^2` on `n=0,2,4,...`; at the fixed point it returns",
        "  `n=0,2,4`.",
        "- The electron exponent is the content number",
        "  `(d+1)(SumY2 Delta_f)=4*5=20`.",
        "- The neutrino mass matrix assembles the prescribed hypercharge-trace",
        "  eigenvalue texture and PMNS rotation. Diagonalisation verifies the",
        "  assembled texture and its absolute Weinberg scale.",
        "",
        "## Primary Chain",
        "",
        "| Key | Current value | Status | Writer | Source |",
        "|---|---:|---|---|---|",
    ]
    lines.extend(parameter_row(parameters, k, m) for k, m in primary)

    lines.extend([
        "",
        "## Cosmology Closure",
        "",
        "The entropy endpoint fixes `H0`; the neutrino floor fixes `rho_Lambda`;",
        "their ratio gives `Omega_Lambda`. The raw photon floor, baryon asymmetry,",
        "and proton mass give `Omega_b`, and flatness gives `Omega_Sigma`. In linear",
        "Boltzmann propagation the residual occupies the cold-source slot. The local",
        "endpoint projection uses `a0` and the stored `mu` response. These two",
        "projections share the endpoint source and are evaluated in their respective",
        "linear-cosmology and local-response branches.",
        "",
        "| Key | Current value | Status | Writer | Source |",
        "|---|---:|---|---|---|",
    ])
    lines.extend(parameter_row(parameters, k, m) for k, m in cosmology)

    lines.extend([
        "",
        "## Formal Verification",
        "",
        f"The archive contains {lean_count} current Lean files. Their finite proofs",
        "verify the implications from the premises declared in each file. Analytic",
        "spectral and continuum premises are supplied in the papers and source",
        "derivations. See `lean_proofs/README.md` for the exact file-level scope.",
        "",
        f"Latest verification verdict: **{verification_verdict()}**.",
        "",
        "## Reproduction",
        "",
        "From the repository root:",
        "",
        "```text",
        "python scripts/reproduce_v4.py",
        "python scripts/audit_param_writers.py",
        "python scripts/audit_observation_leakage.py",
        "python scripts/audit_numeric_precision.py",
        "python scripts/audit_path_portability.py",
        "python -m pytest -q -p no:cacheprovider",
        "python scripts/verify_lean_archive.py --lean-exe <path-to-lean.exe>",
        "```",
        "",
        "`scripts/verify_v4.py` combines these checks and produces",
        "`V4_VERIFICATION_REPORT.md`. All paths recorded in reviewer-facing",
        "artifacts are repository-relative.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    target = DOCS / "V4_LEDGER.md"
    target.write_text(build(), encoding="utf-8")
    print(f"Generated: {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
