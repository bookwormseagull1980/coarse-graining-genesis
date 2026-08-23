# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
scripts/make_reviewer_dashboard.py -- generate a static reviewer dashboard.

The output is a self-contained HTML file for reviewers and Git browsers.  It
visualises the external-input boundary, the prediction/comparison separation,
the fresh-rebuild verification path, and the parameter/module dependency
evidence already present in the repository stores.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
DEFAULT_OUTPUT = ROOT / "docs" / "reviewer_dashboard.html"
SCAN_DIRS = ("cg_core", "cg_frg", "scripts", "comparison")
SOURCE_CALLS = {"get", "sm_value", "get_observed"}
WRITE_CALLS = {"pset", "sm_set", "compare_and_set"}
SELECTED_KEYS = [
    "G_N_PDG", "kL", "M_G", "g2_MG", "g1_MG_geo", "g3_MG_geo",
    "n_generations", "v_HIGGS", "M_Z_pred", "M_W_pred",
    "M_W_pred_lead1loop", "Gamma_b_pred_1loop", "sin2_theta_eff_l_pred",
    "m_H_pred",
    "m_t_pred", "m_e_pred", "Omega_Lambda", "Omega_Sigma",
    "T_CMB_GeV", "T_CMB_corrected_K", "endpoint_sigma8",
    "endpoint_S8", "bbn_Neff",
]
GROUP_ORDER = [
    "scripts", "core", "frg", "gauge", "generation", "ewsb", "fermion",
    "neutrino", "cosmology", "gravity", "qcd", "framework", "comparison",
    "other",
]
SECTOR_LABELS = {
    "scripts": "initialisation",
    "core": "core spectral data",
    "frg": "FRG spine",
    "gauge": "gauge sector",
    "generation": "generation sector",
    "ewsb": "electroweak / EWSB sector",
    "fermion": "fermion masses",
    "neutrino": "neutrino sector",
    "cosmology": "cosmology sector",
    "gravity": "gravity sector",
    "qcd": "QCD sector",
    "framework": "framework checks",
    "comparison": "comparison-only lane",
    "other": "other writers",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def display_path(path_text: str) -> str:
    path = Path(path_text)
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        pass
    if path_text == PY:
        return "python"
    return path_text


def display_command(command: list[str]) -> str:
    parts = []
    for index, item in enumerate(command):
        if index == 0 and item == PY:
            parts.append("python")
        else:
            parts.append(display_path(item))
    return " ".join(parts)


def sanitize_output(text: str) -> str:
    out = text
    for needle in {
        str(ROOT),
        str(ROOT).replace("\\", "/"),
        str(ROOT).replace("\\", "\\\\"),
    }:
        out = out.replace(needle, ".")
    for needle in {PY, PY.replace("\\", "/"), PY.replace("\\", "\\\\")}:
        out = out.replace(needle, "python")
    out = out.replace(".\\.deps", ".deps")
    return out


def run_check(label: str, command: list[str],
              display_cmd: str | None = None) -> dict[str, Any]:
    t0 = time.time()
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = sanitize_output((proc.stdout or "") + (proc.stderr or ""))
    return {
        "label": label,
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "seconds": round(time.time() - t0, 2),
        "command": display_cmd or display_command(command),
        "output": output.strip(),
    }


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def first_string_arg(node: ast.Call) -> str | None:
    if node.args and isinstance(node.args[0], ast.Constant) and \
            isinstance(node.args[0].value, str):
        return node.args[0].value
    return None


class ModuleScan(ast.NodeVisitor):
    def __init__(self) -> None:
        self.reads: set[str] = set()
        self.observed_reads: set[str] = set()
        self.writes: set[str] = set()
        self.sm_writes: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        key = first_string_arg(node)
        if key:
            if name == "get":
                self.reads.add(key)
            elif name in {"sm_value", "get_observed"}:
                self.observed_reads.add(key)
            elif name == "sm_set":
                self.sm_writes.add(key)
            elif name in WRITE_CALLS:
                self.writes.add(key)
        self.generic_visit(node)


def scan_sources() -> dict[str, dict[str, list[str]]]:
    scans: dict[str, dict[str, list[str]]] = {}
    for dirname in SCAN_DIRS:
        base = ROOT / dirname
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue
            visitor = ModuleScan()
            visitor.visit(tree)
            if visitor.reads or visitor.observed_reads or visitor.writes or visitor.sm_writes:
                scans[rel(path)] = {
                    "reads": sorted(visitor.reads),
                    "observed_reads": sorted(visitor.observed_reads),
                    "writes": sorted(visitor.writes),
                    "sm_writes": sorted(visitor.sm_writes),
                }
    return scans


def parse_reproduce_modules() -> list[str]:
    path = ROOT / "scripts" / "reproduce_v4.py"
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "MODULES":
                    return [
                        elt.value for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]
    return []


def module_group(module: str) -> str:
    if module.startswith("cg_frg/"):
        parts = module.split("/")
        return parts[1] if len(parts) > 1 else "cg_frg"
    if module.startswith("cg_core/"):
        return "core"
    if module.startswith("comparison/"):
        return "comparison"
    if module.startswith("scripts/"):
        return "scripts"
    return "other"


def dependency_edges(scans: dict[str, dict[str, list[str]]],
                     cg_params: dict[str, Any]) -> list[dict[str, str]]:
    writer_by_key = {
        key: rec.get("writer")
        for key, rec in cg_params.items()
        if isinstance(rec, dict) and rec.get("writer")
    }
    edges: set[tuple[str, str, str]] = set()
    for module, info in scans.items():
        for key in info.get("reads", []):
            writer = writer_by_key.get(key)
            if writer and writer != module:
                edges.add((writer, module, key))
    return [
        {"from": a, "to": b, "key": k}
        for a, b, k in sorted(edges)
    ]


def build_anchor_tree(module_rows: list[dict[str, Any]],
                      cg_params: dict[str, Any]) -> dict[str, Any]:
    outputs_by_writer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for key, rec in sorted(cg_params.items()):
        if not isinstance(rec, dict):
            continue
        writer = rec.get("writer", "")
        if not writer:
            continue
        outputs_by_writer[writer].append({
            "key": key,
            "value": format_value(rec.get("value")),
            "provenance": rec.get("provenance", ""),
            "role": rec.get("role", ""),
        })

    sectors: list[dict[str, Any]] = []
    seen_writers: set[str] = set()
    for group in GROUP_ORDER:
        modules = []
        for row in module_rows:
            if row["group"] != group:
                continue
            outputs = outputs_by_writer.get(row["module"], [])
            seen_writers.add(row["module"])
            modules.append({
                "index": row["index"],
                "module": row["module"],
                "group": row["group"],
                "reads": row["reads"],
                "observed_reads": row["observed_reads"],
                "outputs": outputs,
            })
        if modules:
            sectors.append({
                "group": group,
                "label": SECTOR_LABELS.get(group, group),
                "output_count": sum(len(m["outputs"]) for m in modules),
                "modules": modules,
            })

    extras = []
    for writer, outputs in sorted(outputs_by_writer.items()):
        if writer in seen_writers or writer == "cg_core.params.init_stores":
            continue
        extras.append({
            "index": None,
            "module": writer,
            "group": "other",
            "reads": [],
            "observed_reads": [],
            "outputs": outputs,
        })
    if extras:
        sectors.append({
            "group": "other",
            "label": SECTOR_LABELS["other"],
            "output_count": sum(len(m["outputs"]) for m in extras),
            "modules": extras,
        })

    return {
        "root": {
            "label": "G_N_PDG",
            "role": "single observed dimensional anchor",
        },
        "trunk": [
            {"label": "init stores", "text": "M_P, tau, seed chain"},
            {"label": "endpoint closure", "text": "kL, M_G, k_GUT"},
            {"label": "sector branches", "text": "derived modules and leaves"},
        ],
        "sectors": sectors,
    }


def verification_verdict() -> str:
    report = ROOT / "V4_VERIFICATION_REPORT.md"
    if not report.exists():
        return "not generated"
    text = report.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"\nPASS\n", text):
        return "PASS"
    if re.search(r"\nFAIL\n", text):
        return "FAIL"
    return "present"


def build_data() -> dict[str, Any]:
    cg_store = load_json(ROOT / "cg_params.json", {"parameters": {}})
    sm_store = load_json(ROOT / "comparison" / "sm_inputs.json", {"parameters": {}})
    write_log = load_json(ROOT / "params_write_log.json", [])
    cg_params = cg_store.get("parameters", {})
    sm_params = sm_store.get("parameters", {})

    provenance = Counter(
        rec.get("provenance", "?")
        for rec in cg_params.values()
        if isinstance(rec, dict)
    )
    roles = Counter(
        rec.get("role", "?")
        for rec in cg_params.values()
        if isinstance(rec, dict)
    )
    writers = Counter(
        rec.get("writer", "?")
        for rec in cg_params.values()
        if isinstance(rec, dict)
    )

    observed_anchors = [
        {"key": key, "value": format_value(rec.get("value")), "writer": rec.get("writer", "")}
        for key, rec in sorted(cg_params.items())
        if isinstance(rec, dict) and rec.get("provenance") == "OBSERVED"
    ]
    scale_choices = [
        {"key": key, "value": format_value(rec.get("value")), "writer": rec.get("writer", "")}
        for key, rec in sorted(cg_params.items())
        if isinstance(rec, dict) and rec.get("provenance") == "SCALE_CHOICE"
    ]
    selected = []
    for key in SELECTED_KEYS:
        rec = cg_params.get(key)
        if isinstance(rec, dict):
            selected.append({
                "key": key,
                "value": format_value(rec.get("value")),
                "provenance": rec.get("provenance", ""),
                "role": rec.get("role", ""),
                "writer": rec.get("writer", ""),
            })

    scans = scan_sources()
    modules = parse_reproduce_modules()
    module_rows = []
    for index, module in enumerate(modules, 1):
        info = scans.get(module, {"reads": [], "observed_reads": [], "writes": [], "sm_writes": []})
        module_rows.append({
            "index": index,
            "module": module,
            "group": module_group(module),
            "reads": info["reads"],
            "observed_reads": info["observed_reads"],
            "writes": info["writes"],
            "sm_writes": info["sm_writes"],
        })

    edges = dependency_edges(scans, cg_params)
    anchor_tree = build_anchor_tree(module_rows, cg_params)
    audit_results = [
        run_check("parameter provenance", [PY, "scripts/audit_param_writers.py"],
                  "python scripts/audit_param_writers.py"),
        run_check("observation leakage", [PY, "scripts/audit_observation_leakage.py"],
                  "python scripts/audit_observation_leakage.py"),
        run_check("Lean source hygiene", [PY, "scripts/audit_lean_sources.py"],
                  "python scripts/audit_lean_sources.py"),
        run_check("numeric precision", [PY, "scripts/audit_numeric_precision.py"],
                  "python scripts/audit_numeric_precision.py"),
        run_check("path portability", [PY, "scripts/audit_path_portability.py"],
                  "python scripts/audit_path_portability.py"),
    ]

    params_table = []
    for key, rec in sorted(cg_params.items()):
        if isinstance(rec, dict):
            params_table.append({
                "key": key,
                "value": format_value(rec.get("value")),
                "provenance": rec.get("provenance", ""),
                "role": rec.get("role", ""),
                "writer": rec.get("writer", ""),
                "note": rec.get("note", ""),
            })

    writer_rows = [
        {"writer": writer, "count": count}
        for writer, count in writers.most_common(18)
    ]

    edge_by_to: dict[str, int] = defaultdict(int)
    for edge in edges:
        edge_by_to[edge["to"]] += 1

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "root": ".",
        "counts": {
            "cg_params": len(cg_params),
            "sm_inputs": len(sm_params),
            "write_log": len(write_log),
            "observed_anchors": len(observed_anchors),
            "scale_choices": len(scale_choices),
            "modules": len(modules),
            "dependency_edges": len(edges),
        },
        "provenance": dict(sorted(provenance.items())),
        "roles": dict(sorted(roles.items())),
        "observed_anchors": observed_anchors,
        "scale_choices": scale_choices,
        "selected": selected,
        "anchor_tree": anchor_tree,
        "modules": module_rows,
        "dependency_edges": edges[:250],
        "module_dependency_counts": edge_by_to,
        "params": params_table,
        "writers": writer_rows,
        "audit_results": audit_results,
        "verification_verdict": verification_verdict(),
    }


def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def dashboard_html(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    observed = data["observed_anchors"][0]["key"] if data["observed_anchors"] else "none"
    audit_ok = all(item["ok"] for item in data["audit_results"])
    status_word = "PASS" if audit_ok else "CHECK"
    return f"""<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
-->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>V4 Reviewer Dashboard</title>
<style>
:root {{
  color-scheme: light dark;
  --bg: #f6f7f9;
  --fg: #20242a;
  --muted: #626b76;
  --panel: #ffffff;
  --line: #d8dee6;
  --blue: #2364aa;
  --green: #168a57;
  --amber: #9a6a00;
  --red: #b4232a;
  --cyan: #0f766e;
  --ink: #111827;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #111418;
    --fg: #e8edf2;
    --muted: #a9b3be;
    --panel: #191f26;
    --line: #35404c;
    --blue: #7cb7ff;
    --green: #6bd39b;
    --amber: #f0c85a;
    --red: #ff8c8c;
    --cyan: #70d5cc;
    --ink: #f8fafc;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.45;
}}
main {{
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 36px;
}}
header {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: end;
  margin-bottom: 18px;
}}
h1, h2, h3, p {{ margin-top: 0; }}
h1 {{ font-size: clamp(26px, 4vw, 42px); line-height: 1.05; margin-bottom: 8px; letter-spacing: 0; }}
h2 {{ font-size: 20px; margin-bottom: 12px; }}
h3 {{ font-size: 15px; margin-bottom: 8px; }}
p {{ color: var(--muted); }}
code {{
  font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
  background: color-mix(in srgb, var(--line) 35%, transparent);
  padding: 2px 5px;
  border-radius: 4px;
}}
.stamp {{ text-align: right; color: var(--muted); font-size: 13px; }}
.grid {{
  display: grid;
  gap: 14px;
}}
.stats {{
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 18px;
}}
.stat {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 14px;
  min-height: 96px;
}}
.label {{ color: var(--muted); font-size: 13px; }}
.value {{ font-size: 26px; font-weight: 650; margin-top: 6px; }}
.ok {{ color: var(--green); }}
.warn {{ color: var(--amber); }}
.bad {{ color: var(--red); }}
section {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
  margin: 14px 0;
}}
.two {{ grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); }}
.three {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.lane {{
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
}}
.box {{
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  min-height: 84px;
}}
.box strong {{ display: block; margin-bottom: 4px; }}
.blue {{ border-color: color-mix(in srgb, var(--blue) 55%, var(--line)); }}
.green {{ border-color: color-mix(in srgb, var(--green) 55%, var(--line)); }}
.gray {{ border-color: var(--line); }}
.redline {{
  border-top: 2px dashed var(--red);
  text-align: center;
  color: var(--red);
  font-size: 12px;
  padding-top: 6px;
  margin-top: 12px;
}}
.root-node {{
  display: grid;
  grid-template-columns: minmax(180px, 260px) minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  margin: 6px 0 14px;
}}
.root-node .anchor {{
  border: 2px solid var(--green);
  border-radius: 8px;
  padding: 12px;
  background: color-mix(in srgb, var(--green) 8%, transparent);
}}
.root-node .anchor strong {{
  display: block;
  margin-bottom: 4px;
}}
.tree-spine {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 12px 0 16px;
}}
.spine-node {{
  position: relative;
  border-top: 4px solid var(--green);
  padding: 10px 10px 8px;
  background: color-mix(in srgb, var(--green) 7%, transparent);
  min-height: 76px;
}}
.spine-node:not(:last-child)::after {{
  content: "->";
  position: absolute;
  right: -16px;
  top: 24px;
  color: var(--muted);
  font-weight: 700;
}}
.tree-branches {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 14px;
  align-items: start;
}}
.sector-branch {{
  border-left: 3px solid var(--blue);
  padding-left: 12px;
}}
.sector-branch[data-group="comparison"] {{ border-left-color: var(--amber); }}
.sector-branch[data-group="ewsb"] {{ border-left-color: var(--green); }}
.sector-branch[data-group="cosmology"] {{ border-left-color: var(--cyan); }}
.sector-branch[data-group="qcd"] {{ border-left-color: var(--red); }}
.sector-head {{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: baseline;
  margin-bottom: 8px;
}}
.sector-head h3 {{ margin: 0; }}
.tree-module {{
  border-top: 1px solid var(--line);
  padding: 10px 0;
}}
.module-title {{
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: baseline;
  margin-bottom: 5px;
}}
.module-title strong,
.module-title span {{
  overflow-wrap: anywhere;
}}
.read-line {{
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 8px;
  overflow-wrap: anywhere;
}}
.leaf-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 7px;
}}
.leaf {{
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 7px;
  min-height: 62px;
  overflow-wrap: anywhere;
  background: color-mix(in srgb, var(--line) 10%, transparent);
}}
.leaf[data-provenance="DERIVED"] {{
  border-color: color-mix(in srgb, var(--blue) 45%, var(--line));
}}
.leaf[data-provenance="OBSERVED"] {{
  border-color: color-mix(in srgb, var(--green) 60%, var(--line));
  background: color-mix(in srgb, var(--green) 7%, transparent);
}}
.leaf[data-provenance="SCALE_CHOICE"] {{
  border-color: color-mix(in srgb, var(--amber) 60%, var(--line));
  background: color-mix(in srgb, var(--amber) 7%, transparent);
}}
.leaf-key {{
  display: block;
  font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  margin-bottom: 4px;
}}
.leaf-value {{
  display: block;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
}}
.tree-empty {{
  color: var(--muted);
  border-top: 1px solid var(--line);
  padding-top: 12px;
}}
.arrow {{ color: var(--muted); font-weight: 700; }}
.timeline {{
  display: grid;
  grid-template-columns: repeat(7, minmax(110px, 1fr));
  gap: 8px;
}}
.step {{
  border-top: 4px solid var(--blue);
  background: color-mix(in srgb, var(--blue) 8%, transparent);
  padding: 10px;
  min-height: 86px;
}}
.step.pass {{ border-color: var(--green); background: color-mix(in srgb, var(--green) 8%, transparent); }}
.step.audit {{ border-color: var(--cyan); background: color-mix(in srgb, var(--cyan) 8%, transparent); }}
.module-strip {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(92px, 1fr));
  gap: 7px;
}}
.module-chip {{
  border: 1px solid var(--line);
  border-left: 5px solid var(--blue);
  border-radius: 6px;
  padding: 7px 8px;
  min-height: 58px;
  font-size: 12px;
  overflow-wrap: anywhere;
}}
.module-chip[data-group="comparison"] {{ border-left-color: var(--amber); }}
.module-chip[data-group="ewsb"] {{ border-left-color: var(--green); }}
.module-chip[data-group="cosmology"] {{ border-left-color: var(--cyan); }}
.module-chip[data-group="qcd"] {{ border-left-color: var(--red); }}
.module-chip small {{ display: block; color: var(--muted); margin-top: 4px; }}
.controls {{
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  margin: 8px 0 12px;
}}
input, select {{
  font: inherit;
  color: var(--fg);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px 10px;
  min-width: 260px;
}}
button {{
  font: inherit;
  border: 1px solid var(--line);
  background: var(--panel);
  color: var(--fg);
  border-radius: 6px;
  padding: 8px 10px;
  cursor: pointer;
}}
button[aria-pressed="true"] {{ border-color: var(--blue); color: var(--blue); }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
th, td {{
  border-bottom: 1px solid var(--line);
  padding: 8px 7px;
  text-align: left;
  vertical-align: top;
}}
th {{ color: var(--muted); font-weight: 650; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.table-wrap {{ overflow-x: auto; }}
.pill {{
  display: inline-block;
  padding: 2px 7px;
  border-radius: 999px;
  border: 1px solid var(--line);
  font-size: 12px;
  white-space: nowrap;
}}
.pill.good {{ color: var(--green); border-color: color-mix(in srgb, var(--green) 50%, var(--line)); }}
.pill.compare {{ color: var(--amber); border-color: color-mix(in srgb, var(--amber) 50%, var(--line)); }}
.detail {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}}
.list {{
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
  min-height: 120px;
  overflow-wrap: anywhere;
}}
.list ul {{ margin: 6px 0 0; padding-left: 18px; }}
.list li {{ margin-bottom: 4px; }}
.bar-row {{
  display: grid;
  grid-template-columns: minmax(120px, 240px) 1fr auto;
  gap: 9px;
  align-items: center;
  margin: 7px 0;
  font-size: 13px;
}}
.bar-track {{ height: 10px; background: color-mix(in srgb, var(--line) 50%, transparent); }}
.bar-fill {{ height: 100%; background: var(--blue); }}
pre {{
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: color-mix(in srgb, var(--line) 22%, transparent);
  border-radius: 8px;
  padding: 10px;
  font-size: 12px;
  max-height: 220px;
  overflow: auto;
}}
@media (max-width: 860px) {{
  header, .two, .three, .detail, .stats {{ grid-template-columns: 1fr; }}
  .stamp {{ text-align: left; }}
  .lane {{ grid-template-columns: 1fr; }}
  .arrow {{ display: none; }}
  .timeline, .tree-spine, .root-node {{ grid-template-columns: 1fr; }}
  .spine-node:not(:last-child)::after {{ content: ""; }}
  input, select {{ min-width: 100%; }}
}}
</style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>V4 Reviewer Dashboard</h1>
      <p>External input boundary, prediction/comparison separation, and dependency evidence generated from the current repository stores.</p>
    </div>
    <div class="stamp">Generated {esc(data["generated_at"])}<br>Status <strong class="{'ok' if audit_ok else 'bad'}">{status_word}</strong></div>
  </header>

  <div class="grid stats">
    <div class="stat"><div class="label">Allowed observed anchor</div><div class="value">{esc(data["counts"]["observed_anchors"])}</div><div><code>{esc(observed)}</code></div></div>
    <div class="stat"><div class="label">Prediction records</div><div class="value">{esc(data["counts"]["cg_params"])}</div><div class="label">from <code>cg_params.json</code></div></div>
    <div class="stat"><div class="label">Comparison records</div><div class="value">{esc(data["counts"]["sm_inputs"])}</div><div class="label">quarantined to <code>comparison/</code></div></div>
    <div class="stat"><div class="label">Observed leakage audit</div><div class="value {'ok' if audit_ok else 'bad'}">{status_word}</div><div class="label">0 prediction-context violations expected</div></div>
  </div>

  <section>
    <h2>1. External-input firewall</h2>
    <div class="grid two">
      <div>
        <div class="lane">
          <div class="box green"><strong>Allowed external input</strong><code>{esc(observed)}</code><br><span class="label">sets the dimensional Planck scale</span></div>
          <div class="arrow">-></div>
          <div class="box blue"><strong>Prediction chain</strong><code>scripts/reproduce_v4.py</code><br><code>cg_core/</code> + <code>cg_frg/</code></div>
        </div>
        <div class="lane" style="margin-top:12px">
          <div class="box gray"><strong>Observed SM values</strong><code>comparison/sm_inputs.json</code><br><span class="label">central values and bounds for comparison</span></div>
          <div class="arrow">-></div>
          <div class="box gray"><strong>Post-prediction comparison</strong><code>comparison/param_audit_full.py</code><br><span class="label">deviation table only</span></div>
        </div>
        <div class="redline">Forbidden direction audited: comparison/observed values -> prediction modules</div>
      </div>
      <div>
        <h3>Current input classification</h3>
        <div id="inputSummary"></div>
      </div>
    </div>
  </section>

  <section>
    <h2>2. Anchor-to-results tree</h2>
    <div class="root-node">
      <div class="anchor">
        <strong>root anchor</strong>
        <code>{esc(observed)}</code>
        <div class="label">the only observed dimensional anchor in the prediction store</div>
      </div>
      <p>Each branch is a reproducible sector in <code>scripts/reproduce_v4.py</code>. Leaves are the actual parameter records written into <code>cg_params.json</code>, not a hand-picked illustration.</p>
    </div>
    <div id="treeSpine" class="tree-spine"></div>
    <div class="controls">
      <label for="treeSector">Sector</label>
      <select id="treeSector"></select>
      <input id="treeSearch" type="search" placeholder="Search module, input, or result">
      <span class="label" id="treeCount"></span>
    </div>
    <div id="anchorTree" class="tree-branches"></div>
  </section>

  <section>
    <h2>3. Fresh rebuild verification path</h2>
    <div class="timeline">
      <div class="step">delete<br><code>cg_params.json</code></div>
      <div class="step">delete<br><code>sm_inputs.json</code></div>
      <div class="step">delete<br><code>params_write_log.json</code></div>
      <div class="step pass">run<br><code>reproduce_v4.py</code></div>
      <div class="step audit">audit<br>provenance</div>
      <div class="step audit">audit<br>observation leakage</div>
      <div class="step pass">compare + test<br><code>PASS</code></div>
    </div>
    <p style="margin-top:12px">Latest report verdict detected in this checkout: <strong>{esc(data["verification_verdict"])}</strong>. Regenerate with <code>py scripts/verify_v4.py --fresh --audit --pytest --stability --report V4_VERIFICATION_REPORT.md</code>. Add <code>--lean</code> when Lean 4.7 is available.</p>
  </section>

  <section>
    <h2>4. Prediction chain modules</h2>
    <p>The strip follows the module order in <code>scripts/reproduce_v4.py</code>. Each tile shows static reads and writes found in source.</p>
    <div id="moduleStrip" class="module-strip"></div>
    <div class="controls">
      <label for="moduleSelect">Inspect module</label>
      <select id="moduleSelect"></select>
    </div>
    <div id="moduleDetail" class="detail"></div>
  </section>

  <section>
    <h2>5. Parameter provenance and selected predictions</h2>
    <div class="grid two">
      <div>
        <h3>Provenance mix</h3>
        <div id="provenanceBars"></div>
        <h3 style="margin-top:16px">Top writer modules</h3>
        <div id="writerBars"></div>
      </div>
      <div>
        <h3>Selected closed values</h3>
        <div class="table-wrap"><table id="selectedTable"></table></div>
      </div>
    </div>
  </section>

  <section>
    <h2>6. Full parameter browser</h2>
    <div class="controls">
      <input id="paramSearch" type="search" placeholder="Search key, writer, provenance, or note">
      <button type="button" id="derivedOnly" aria-pressed="false">DERIVED only</button>
      <span class="label" id="paramCount"></span>
    </div>
    <div class="table-wrap"><table id="paramTable"></table></div>
  </section>

  <section>
    <h2>7. Audit outputs</h2>
    <div id="auditOutputs" class="grid three"></div>
  </section>
</main>

<script>
const DATA = {payload};

function el(tag, attrs = {{}}, children = []) {{
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {{
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }});
  children.forEach(child => node.appendChild(child));
  return node;
}}

function renderInputSummary() {{
  const root = document.getElementById("inputSummary");
  const anchors = DATA.observed_anchors.map(a => `<tr><td><code>${{a.key}}</code></td><td>${{a.value}}</td><td>${{a.writer}}</td></tr>`).join("");
  const scale = DATA.scale_choices.map(a => `<tr><td><code>${{a.key}}</code></td><td>${{a.value}}</td><td>${{a.writer}}</td></tr>`).join("");
  root.innerHTML = `
    <table>
      <thead><tr><th>class</th><th>key/value</th><th>writer</th></tr></thead>
      <tbody>
        ${{anchors ? anchors.replaceAll("<tr>", "<tr><td><span class='pill good'>OBSERVED</span></td>") : "<tr><td><span class='pill good'>OBSERVED</span></td><td>none</td><td></td></tr>"}}
        ${{scale ? scale.replaceAll("<tr>", "<tr><td><span class='pill'>SCALE_CHOICE</span></td>") : ""}}
      </tbody>
    </table>`;
}}

function renderTreeSpine() {{
  const root = document.getElementById("treeSpine");
  root.innerHTML = "";
  (DATA.anchor_tree.trunk || []).forEach((node, index) => {{
    const block = el("div", {{"class": "spine-node"}});
    block.appendChild(el("strong", {{text: String(index + 1) + ". " + node.label}}));
    block.appendChild(el("div", {{"class": "label", text: node.text}}));
    root.appendChild(block);
  }});
}}

function renderTreeControls() {{
  const select = document.getElementById("treeSector");
  select.innerHTML = "";
  select.appendChild(el("option", {{value: "all", text: "all sectors"}}));
  (DATA.anchor_tree.sectors || []).forEach(sector => {{
    const text = sector.label + " (" + sector.output_count + ")";
    select.appendChild(el("option", {{value: sector.group, text}}));
  }});
  select.addEventListener("change", renderAnchorTree);
  document.getElementById("treeSearch").addEventListener("input", renderAnchorTree);
}}

function leafMatches(leaf, query) {{
  const hay = [leaf.key, leaf.value, leaf.provenance, leaf.role].join(" ").toLowerCase();
  return hay.includes(query);
}}

function moduleText(module) {{
  return [module.module].concat(module.reads || []).concat(module.observed_reads || []).join(" ").toLowerCase();
}}

function readLine(module) {{
  const reads = module.reads || [];
  const observed = module.observed_reads || [];
  const pieces = [];
  if (reads.length) {{
    const shown = reads.slice(0, 8).join(", ");
    pieces.push("reads: " + shown + (reads.length > 8 ? " +" + String(reads.length - 8) : ""));
  }}
  if (observed.length) {{
    pieces.push("observed reads: " + observed.join(", "));
  }}
  return pieces.length ? pieces.join(" | ") : "no upstream framework reads detected";
}}

function makeLeaf(leaf) {{
  const node = el("div", {{"class": "leaf", "data-provenance": leaf.provenance || ""}});
  node.appendChild(el("span", {{"class": "leaf-key", text: leaf.key}}));
  node.appendChild(el("span", {{"class": "leaf-value", text: leaf.value}}));
  node.appendChild(el("span", {{"class": "label", text: leaf.provenance || "unknown"}}));
  return node;
}}

function renderAnchorTree() {{
  const root = document.getElementById("anchorTree");
  const selected = document.getElementById("treeSector").value;
  const query = document.getElementById("treeSearch").value.trim().toLowerCase();
  root.innerHTML = "";
  let shownModules = 0;
  let shownLeaves = 0;

  (DATA.anchor_tree.sectors || []).forEach(sector => {{
    if (selected !== "all" && sector.group !== selected) return;
    const sectorModules = [];
    (sector.modules || []).forEach(module => {{
      const outputs = module.outputs || [];
      const moduleHit = !query || moduleText(module).includes(query);
      const leaves = query && !moduleHit ? outputs.filter(leaf => leafMatches(leaf, query)) : outputs;
      if (query && !moduleHit && leaves.length === 0) return;
      sectorModules.push({{module, leaves}});
    }});
    if (!sectorModules.length) return;

    const branch = el("div", {{"class": "sector-branch", "data-group": sector.group}});
    const branchLeaves = sectorModules.reduce((total, row) => total + row.leaves.length, 0);
    const head = el("div", {{"class": "sector-head"}});
    head.appendChild(el("h3", {{text: sector.label}}));
    head.appendChild(el("span", {{"class": "label", text: String(branchLeaves) + " leaves"}}));
    branch.appendChild(head);

    sectorModules.forEach(row => {{
      const module = row.module;
      const box = el("div", {{"class": "tree-module"}});
      const title = el("div", {{"class": "module-title"}});
      const prefix = module.index ? String(module.index) + ". " : "";
      title.appendChild(el("strong", {{text: prefix + module.module}}));
      title.appendChild(el("span", {{"class": "label", text: String(row.leaves.length) + " outputs"}}));
      box.appendChild(title);
      box.appendChild(el("div", {{"class": "read-line", text: readLine(module)}}));
      const leaves = el("div", {{"class": "leaf-grid"}});
      if (row.leaves.length) {{
        row.leaves.forEach(leaf => leaves.appendChild(makeLeaf(leaf)));
      }} else {{
        leaves.appendChild(el("div", {{"class": "label", text: "no stored outputs"}}));
      }}
      box.appendChild(leaves);
      branch.appendChild(box);
      shownModules += 1;
      shownLeaves += row.leaves.length;
    }});
    root.appendChild(branch);
  }});

  document.getElementById("treeCount").textContent =
    String(shownModules) + " modules, " + String(shownLeaves) + " leaves shown";
  if (!root.children.length) {{
    root.appendChild(el("div", {{"class": "tree-empty", text: "no branch matches the current filter"}}));
  }}
}}

function renderModuleStrip() {{
  const root = document.getElementById("moduleStrip");
  root.innerHTML = "";
  DATA.modules.forEach(m => {{
    const short = m.module.split("/").slice(-2).join("/");
    root.appendChild(el("div", {{"class": "module-chip", "data-group": m.group}}, [
      el("strong", {{text: `${{m.index}}. ${{short}}`}}),
      el("small", {{text: `${{m.writes.length}} writes, ${{m.reads.length}} reads`}})
    ]));
  }});

  const select = document.getElementById("moduleSelect");
  DATA.modules.forEach((m, i) => {{
    select.appendChild(el("option", {{value: String(i), text: `${{m.index}}. ${{m.module}}`}}));
  }});
  select.addEventListener("change", renderModuleDetail);
  renderModuleDetail();
}}

function listBlock(title, values, extraClass = "") {{
  const block = el("div", {{"class": `list ${{extraClass}}`}});
  block.appendChild(el("strong", {{text: title}}));
  if (!values || values.length === 0) {{
    block.appendChild(el("p", {{"class": "label", text: "none detected"}}));
    return block;
  }}
  const ul = el("ul");
  values.slice(0, 80).forEach(v => ul.appendChild(el("li", {{text: v}})));
  if (values.length > 80) ul.appendChild(el("li", {{text: `... ${{values.length - 80}} more`}}));
  block.appendChild(ul);
  return block;
}}

function renderModuleDetail() {{
  const index = Number(document.getElementById("moduleSelect").value || 0);
  const m = DATA.modules[index];
  const root = document.getElementById("moduleDetail");
  root.innerHTML = "";
  const upstream = DATA.dependency_edges.filter(e => e.to === m.module).map(e => `${{e.key}} <- ${{e.from}}`);
  root.appendChild(listBlock("Framework reads", m.reads));
  root.appendChild(listBlock("Framework writes", m.writes));
  root.appendChild(listBlock("Upstream dependencies", upstream));
  if (m.observed_reads.length) {{
    root.appendChild(listBlock("Observed reads", m.observed_reads, "bad"));
  }}
}}

function bars(rootId, rows, colorClass = "") {{
  const root = document.getElementById(rootId);
  root.innerHTML = "";
  const max = Math.max(1, ...rows.map(r => r.count));
  rows.forEach(r => {{
    const row = el("div", {{"class": "bar-row"}});
    row.appendChild(el("div", {{text: r.label || r.writer}}));
    const track = el("div", {{"class": "bar-track"}});
    const fill = el("div", {{"class": "bar-fill"}});
    fill.style.width = `${{Math.max(2, r.count / max * 100)}}%`;
    if (colorClass === "green") fill.style.background = "var(--green)";
    if (colorClass === "amber") fill.style.background = "var(--amber)";
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(el("div", {{"class": "num", text: String(r.count)}}));
    root.appendChild(row);
  }});
}}

function renderTables() {{
  const provRows = Object.entries(DATA.provenance).map(([label, count]) => ({{label, count}}));
  bars("provenanceBars", provRows, "green");
  bars("writerBars", DATA.writers.map(w => ({{writer: w.writer, count: w.count}})), "");

  const selected = document.getElementById("selectedTable");
  selected.innerHTML = `<thead><tr><th>key</th><th>value</th><th>provenance</th><th>writer</th></tr></thead><tbody>${{
    DATA.selected.map(r => `<tr><td><code>${{r.key}}</code></td><td class="num">${{r.value}}</td><td><span class="pill good">${{r.provenance}}</span></td><td>${{r.writer}}</td></tr>`).join("")
  }}</tbody>`;
}}

function renderParams() {{
  const q = document.getElementById("paramSearch").value.toLowerCase();
  const derived = document.getElementById("derivedOnly").getAttribute("aria-pressed") === "true";
  let rows = DATA.params.filter(r => {{
    if (derived && r.provenance !== "DERIVED") return false;
    const hay = `${{r.key}} ${{r.value}} ${{r.provenance}} ${{r.role}} ${{r.writer}} ${{r.note}}`.toLowerCase();
    return hay.includes(q);
  }});
  document.getElementById("paramCount").textContent = `${{rows.length}} shown`;
  rows = rows.slice(0, 160);
  document.getElementById("paramTable").innerHTML = `<thead><tr><th>key</th><th>value</th><th>provenance</th><th>role</th><th>writer</th></tr></thead><tbody>${{
    rows.map(r => `<tr><td><code>${{r.key}}</code></td><td class="num">${{r.value}}</td><td>${{r.provenance}}</td><td>${{r.role}}</td><td>${{r.writer}}</td></tr>`).join("")
  }}</tbody>`;
}}

function renderAudits() {{
  const root = document.getElementById("auditOutputs");
  root.innerHTML = "";
  DATA.audit_results.forEach(a => {{
    const card = el("div", {{"class": "box"}});
    card.appendChild(el("h3", {{text: a.label}}));
    card.appendChild(el("div", {{"class": a.ok ? "ok" : "bad", text: a.ok ? "PASS" : "FAIL"}}));
    card.appendChild(el("p", {{"class": "label", text: `${{a.seconds}}s, exit ${{a.returncode}}`}}));
    card.appendChild(el("pre", {{text: a.output || "(no output)"}}));
    root.appendChild(card);
  }});
}}

document.getElementById("paramSearch").addEventListener("input", renderParams);
document.getElementById("derivedOnly").addEventListener("click", event => {{
  const pressed = event.currentTarget.getAttribute("aria-pressed") === "true";
  event.currentTarget.setAttribute("aria-pressed", String(!pressed));
  renderParams();
}});

renderInputSummary();
renderTreeSpine();
renderTreeControls();
renderAnchorTree();
renderModuleStrip();
renderTables();
renderParams();
renderAudits();
</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the V4 reviewer dashboard HTML.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="output HTML path")
    args = parser.parse_args()

    out = args.output if args.output.is_absolute() else ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        out.resolve().relative_to(ROOT.resolve())
        if out.exists():
            out.unlink()
    except (OSError, ValueError):
        pass
    data = build_data()
    out.write_text(dashboard_html(data), encoding="utf-8")
    try:
        shown = out.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        shown = str(out)
    print(f"reviewer dashboard written: {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
