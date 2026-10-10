# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Evaluate the current finite, source, matching and propagation extensions.

Each result declares its inputs, response operator and physical scope.
The record includes production readouts and specified finite-operator examples.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cg_core.release import publication_metadata
from cg_frg.neutrino.complex_mixing import evaluate_records as mixing
from cg_core.joint_response import evaluate_records as joint
from cg_core.params import (prediction_inputs_only, PredictionRecords, input_scope,
    record, value_fingerprint, resolve_value, store_root)
from cg_core.finite_connector import evaluate_native_operations
from cg_core.source_response import (evaluate_endpoint_response, certify_affine_residue,
                                    evaluate_bandwidth_response, evaluate_hierarchy_selection)
from comparison.sm_rge.inputs import (published_running_mass_benchmark,
                                      joint_comparison_input_fingerprints, neutron_helium_benchmark)
from scripts.validate_endpoint_cosmology import registered_scale_diagnostic
from cg_core.matter_matching import evaluate_matter_extensions
from cg_frg.qcd.qcd_sector import three_quark_source_certificate
from cg_frg.gravity.matter_source_response import (
    evaluate_matter_source_response, evaluate_common_source_background,
    evaluate_common_source_reuse, evaluate_plane_common_source,
    evaluate_expanding_rms_window)
from cg_frg.cosmology.gw_ratio import C_MS, GEV_TO_S
from cg_frg.cosmology.camb_interface import thermal_history_distance_budget
from cg_frg.gravity.external_tensor import evaluate_records as external_tensor
from cg_frg.ewsb.native_condensate import (
    solve_native_condensate, intensity_response_certificate, solve_joint_native_condensate)
from cg_core.rational_interval import Interval
from cg_frg.frg.discrete_flow import free_carrier_checks
from cg_frg.neutrino.complex_mixing import pmns_texture
from cg_frg.neutrino.propagation import (hamiltonian, propagate_layers,
    propagate_profile, beta_mass_observables)
from cg_frg.gravity.local_response import (background_response,
    gaussian_disk_source, solve_dirichlet, local_source_decomposition, evolve_plane_source,
    evaluate_covariant_clock)


def propagation_example(records):
    """Current rest spectrum; explicit vacuum baseline, no environmental fit."""
    value = lambda key: float(records[key]["value"])
    masses = [value("m_nu1"), value("m_nu2"), value("m_nu3")]
    u = pmns_texture(delta=math.pi*value("cp_pmns_87_pattern"))
    energy, length = 3e6, 2e9
    h = hamiltonian(masses, u, energy)
    exact = propagate_layers([(length, h)])
    numerical = propagate_profile(lambda x: h, length)
    residual = float(np.max(np.abs(exact["probabilities"]-numerical["probabilities"])))
    passed = residual < 1e-8 and numerical["unitarity_residual"] < 1e-8
    if not passed:
        raise ArithmeticError("labelled propagation comparison failed")
    return {"scope": "vacuum example using the current static masses and labelled PMNS texture",
            "inputs": {"masses_eV": masses, "energy_eV": energy,
                       "length_eV_inverse": length, "majorana_phases": [0., 0.],
                       "dirac_phase": math.pi*value("cp_pmns_87_pattern"),
                       "matter_potential": "zero", "additional_source": "zero"},
            "probability_convention": exact["probability_convention"],
            "probabilities": exact["probabilities"].tolist(),
            "profile_probability_residual": residual,
            "unitarity_residual": numerical["unitarity_residual"],
            "beta_mass_observables": beta_mass_observables(masses, u),
            "passed": passed}


def local_example():
    """Non-spherical finite source with specified box, units and boundary."""
    source = gaussian_disk_source(mass=.015, radial_width=.22, vertical_width=.12)
    rows = []
    for n in (4, 6):
        solution = solve_dirichlet(source, lambda x: .1*x[:, 0], n=n,
                                   a0=.3, epsilon=0., tolerance=2e-10)
        parts = local_source_decomposition(solution)
        rows.append({"subdivisions_per_axis": n,
                     "weak_residual_inf": solution["weak_residual_inf"],
                     "source_integral": solution["source_integral"],
                     "flux_balance_residual": solution["flux_balance_residual"],
                     "source_identity_residual": parts["identity_residual"],
                     "interior_source_residual": parts["interior_source_residual"],
                     "minimum_potential": float(np.min(solution["phi"])),
                     "iterations": solution["iterations"]})
    passed = all(r["weak_residual_inf"] < 2e-10
                 and r["interior_source_residual"] < 2e-10
                 and abs(r["flux_balance_residual"]) < 1e-8 for r in rows)
    if not passed:
        raise ArithmeticError("finite local source calculation failed")
    background = background_response([.1, 0., 0.], a0=.3)
    background["principal_tensor"] = background["principal_tensor"].tolist()
    return {"scope": "unregularized finite-box static example; nodal loads with boundary reactions",
            "inputs": {"unit_convention": "specified length/potential units with 4*pi*G=1",
                       "box_lengths": [1., 1., 1.], "whole_space_mass": .015,
                       "radial_width": .22, "vertical_width": .12,
                       "centre": [.5, .5, .5], "boundary_potential": "0.1*x",
                       "a0": .3, "epsilon": 0., "free_cold_source": 0.},
            "mesh_evaluations": rows,
            "mesh_difference_is_error_certificate": False,
            "background_response": background,
            "homogeneous_to_local_source_map": "requires separate evolution and averaging",
            "passed": passed}


def local_feedback_example():
    """Finite plane source and its self-consistent nonlinear potential, per unit area."""
    positions = np.linspace(0., 1., 9)
    midpoints = (positions[:-1]+positions[1:])/2
    masses = .1*np.diff(positions)*(1+.2*np.cos(2*math.pi*midpoints)
                                   +.1*np.sin(2*math.pi*midpoints))
    velocity = .02*np.sin(math.pi*positions)
    velocity[[0,-1]] = 0.
    rows = []
    for steps in (20,40):
        result = evolve_plane_source(positions, masses, velocity, duration=.4,
                                     steps=steps, a0=.3, four_pi_G=1.)
        rows.append({"time_steps": steps, "time_step": result["time_step"],
                     "final_positions": result["positions"][-1].tolist(),
                     "final_velocities": result["velocities"][-1].tolist(),
                     "final_density": result["final_density"].tolist(),
                     "initial_energy": float(result["total_energy"][0]),
                     "final_energy": float(result["total_energy"][-1]),
                     "final_boundary_work": float(result["boundary_work"][-1]),
                     **{key: result[key] for key in (
                         "maximum_energy_balance_residual", "energy_identity_residual",
                         "boundary_residual", "mass_conservation_residual",
                         "minimum_cell_length", "operation_counts")}})
    coarse,fine = rows
    ratio = coarse["maximum_energy_balance_residual"]/fine["maximum_energy_balance_residual"]
    position_difference = float(np.max(np.abs(np.asarray(coarse["final_positions"])
                                             -np.asarray(fine["final_positions"]))))
    passed = (2.5 < ratio < 5.5 and position_difference < 1e-6 and all(
        row["maximum_energy_balance_residual"] < 1e-9
        and row["mass_conservation_residual"] < 1e-13
        and row["boundary_residual"] < 1e-11
        and row["energy_identity_residual"] < 1e-12
        and row["minimum_cell_length"] > .1 for row in rows))
    if not passed:
        raise ArithmeticError("finite source-potential evolution failed its conservation or refinement check")
    return {"scope": "self-consistent finite plane material cells before trajectory crossing",
            "inputs": {"unit_convention": "fixed length, time and mass units with 4*pi*G=1",
                       "a0": .3, "duration": .4, "initial_positions": positions.tolist(),
                       "cell_masses": masses.tolist(), "initial_velocity": velocity.tolist(),
                       "boundary_potential": [0.,0.], "boundary_velocity": [0.,0.],
                       "quadrature_order": 24},
            "field_equation": "d_x[mu(abs(d_x Phi)/a0)*d_x Phi]=4*pi*G*rho",
            "energy": "kinetic + source + nonlinear field, per unit transverse area",
            "spatial_discretization": "affine material cells with their consistent mass matrix",
            "time_discretization": "velocity Verlet; two step sizes at fixed material resolution",
            "evaluations": rows, "energy_error_reduction_factor": ratio,
            "final_position_difference": position_difference,
            "passed": bool(passed)}


def exact_affine_examples():
    """Exact finite response examples with their full declared coefficients."""
    cases = {
        "visible_kernel": ([[0, 0], [0, 2]], [[2, 1], [1, 2]], [[1], [1]], Fraction(1, 2)),
        "positive_mass": ([[Fraction(1, 10**12), 0], [0, 2]], [[1, 0], [0, 1]], [[1], [0]], Fraction(0)),
        "source_invisible_kernel": ([[0, 0], [0, 2]], [[1, 0], [0, 1]], [[0], [1]], Fraction(0)),
    }
    matrix = lambda a: [[str(Fraction(x)) for x in row] for row in a]
    results = {}
    for name, (H, K, S, expected) in cases.items():
        certificate = certify_affine_residue(H, K, S)
        passed = (certificate["kernel_identity_verified"]
                  and certificate["residue"][0, 0] == expected
                  and certificate["finite_positive_measure_certified"])
        results[name] = {
            "inputs": {"H": matrix(H), "K": matrix(K), "S": matrix(S)},
            "kernel_basis": matrix(certificate["kernel_basis"]),
            "critical_slope": matrix(certificate["critical_slope"]),
            "residue": matrix(certificate["residue"]),
            "kernel_dimension": certificate["kernel_dimension"],
            "visible_rank": certificate["visible_rank"],
            "complement_gap_lower_bound": str(certificate["complement_gap_lower_bound"]),
            "algebraic_pole_established": certificate["algebraic_pole_established"],
            "finite_positive_measure_certified": certificate["finite_positive_measure_certified"],
            "physical_atom_established": False,
            "passed": passed}
    return {"scope": "exact rational certificates for the declared finite affine responses",
            "coefficient_convention": "rational strings; no floating-point zero threshold",
            "examples": results, "passed": all(row["passed"] for row in results.values())}


def native_intensity_example(records):
    """One declared native scalar branch, sharing a single root certificate."""
    inputs = {"g":"1", "Z":"2", "L":"2.5", "shells":128, "iterations":55}
    stationary = solve_native_condensate(**inputs)
    response = intensity_response_certificate("0.1",
        amplitude_squared=Interval.bounds(*stationary["amplitude_squared"]),
        mass_squared=Interval.bounds(*stationary["mass_squared"]),
        Z=inputs["Z"], L=inputs["L"], shells=16, terms=24)
    joint = solve_joint_native_condensate(g=inputs["g"], Z=inputs["Z"],
                                          shells=inputs["shells"], iterations=inputs["iterations"])
    value = lambda key: float(records[key]["value"])
    response_unit, planck = value("M_G"), value("M_P")
    occupied = evaluate_common_source_background(
        joint_certificate=joint, planck_ratio=planck/response_unit,
        mass_squared=3/(8*math.pi),
        vacuum_density=value("Lambda")*planck**2/response_unit**4)
    occupied["physical_normalization"] = {
        "response_mass_unit": "M_G", "response_mass_unit_GeV": response_unit,
        "vacuum_density": "Lambda*M_P^2",
        "retained_pair": "two real constant-shell coordinates of the scalar doublet at zero connection",
        "reference_mass_squared": "3/(4*L_ref^2), L_ref^2=2*pi"}
    occupied["source_reuse_experiment"] = evaluate_common_source_reuse(background=occupied)
    occupied["planar_evolution"] = evaluate_plane_common_source(background=occupied)
    passed = (stationary["strict_positive_gap_certified"]
              and response["strict_positive_atom_certified"]
              and response["infinite_internal_tail_included"] and joint["passed"]
              and occupied["passed"] and occupied["source_reuse_experiment"]["passed"]
              and occupied["planar_evolution"]["passed"])
    return {"scope":"explicit g,Z,L realization of the native quadratic scalar intensity",
            "inputs":inputs, "stationary":stationary, "intensity":response,
            "joint_collective_source":joint,
            "occupied_common_background":occupied,
            "stationary_certificate_evaluations":1,
            "total_distinct_stationary_certificate_evaluations":2,
            "assigned_production_mass":False, "passed":passed}


def undeformed_branch_check(records):
    """Check the production branch against the analytic denominator margin."""
    from cg_core.spectrum_loop import iter_sm_spectrum
    from cg_frg.frg.spectral_sum import _w_tmunu_spin2
    value = lambda key: float(records[key]["value"])
    c, k, tau = value("kL"), value("M_G")/value("M_P"), value("tau")
    weight_count = sum(deg*_w_tmunu_spin2(kind, name)
        for kind, name, _, _, _, deg in iter_sm_spectrum(1., math.sqrt(math.pi), tau))
    x0 = value("chi_pole_x0")
    upper, margin = Fraction(162500, 172543), Fraction(10043, 172543)
    branch_matches = weight_count == 2080 and math.isclose(c*k, math.sqrt(math.pi), rel_tol=1e-12)
    passed = branch_matches and 0 <= x0 < float(upper) and 1-x0 > float(margin)
    return {"scope": "undeformed three-generation R=5 compact scalar ladder",
            "inputs": {"c": c, "k": k, "tau": tau, "chi": 0.},
            "weighted_retained_multiplicity": weight_count,
            "x0": x0, "denominator_margin": 1-x0,
            "analytic_x0_upper_bound": "65/(7*pi^2)",
            "rational_x0_upper_bound": str(upper),
            "rational_denominator_margin_lower_bound": str(margin),
            "rational_bound_input": "pi > 157/50",
            "radius_dependence_of_x": "none on the fixed dimensionless branch",
            "radius_closure_selects_detuning": False,
            "external_scalar_continuation": "analytic Pi(z), x(z), with x(0)=x0, has zero residue",
            "full_tensor_kernel_computed": False,
            "passed": passed}


RESPONSE_NAMES = (
    "joint_response", "endpoint_source_response", "native_operations", "matter_extensions",
    "finite_matter_source", "neutrino_propagation", "local_static_response", "free_covariance",
    "complex_mixing", "exact_affine_certificates", "undeformed_branch_margin",
    "external_gauge_tensor", "native_scalar_intensity", "bandwidth_response",
    "local_source_feedback")

# Entry modules for each evaluation below. Imports inside these modules, including
# function-local imports and package initializers, are followed transitively.
# The driver itself is common to all responses, without treating its unrelated
# entry-point imports as dependencies of every individual calculation.
_RESPONSE_MODULES = {
    "joint_response": ("cg_core.joint_response", "cg_core.matter_matching", "cg_frg.qcd.qcd_sector",
                       "comparison.sm_rge.inputs", "scripts.validate_endpoint_cosmology"),
    "endpoint_source_response": ("cg_core.source_response",),
    "native_operations": ("cg_core.finite_connector",),
    "matter_extensions": ("cg_core.matter_matching",),
    "finite_matter_source": ("cg_frg.gravity.matter_source_response",),
    "neutrino_propagation": ("cg_frg.neutrino.complex_mixing", "cg_frg.neutrino.propagation"),
    "local_static_response": ("cg_frg.gravity.local_response",),
    "free_covariance": ("cg_frg.frg.discrete_flow",),
    "complex_mixing": ("cg_frg.neutrino.complex_mixing",),
    "exact_affine_certificates": ("cg_core.source_response",),
    "undeformed_branch_margin": ("cg_core.spectrum_loop", "cg_frg.frg.spectral_sum"),
    "external_gauge_tensor": ("cg_frg.gravity.external_tensor",),
    "native_scalar_intensity": ("cg_frg.ewsb.native_condensate", "cg_core.rational_interval",
                                "cg_frg.gravity.matter_source_response"),
    "bandwidth_response": ("cg_core.source_response",),
    "local_source_feedback": ("cg_frg.gravity.local_response",
                              "cg_frg.gravity.matter_source_response",
                              "cg_frg.cosmology.gw_ratio"),
}
_COMMON_RESPONSE_MODULES = ("cg_core.params", "cg_core.sm_content", "cg_core.window_weights")


class _ResponseSourceGraph:
    """Read each source once per identity snapshot; conservatively follow imports.

    Source identities concern project Python code. Direct parameter/reference
    inputs and the installed numerical environment retain their separate run
    identities. Dynamic loading or an unresolved local import selects the whole
    project source set rather than asserting an incomplete dependency closure.
    """

    packages = ("cg_core", "cg_frg", "comparison", "scripts")

    def __init__(self, root):
        self.root = root
        self.contents = {}
        self.digests = {}
        self.imports = {}

    def _source(self, path):
        if path not in self.contents:
            self.contents[path] = path.read_bytes()
            self.digests[path] = hashlib.sha256(self.contents[path]).hexdigest()
        return self.contents[path]

    def _module_path(self, module):
        base = self.root.joinpath(*module.split("."))
        for path in (base.with_suffix(".py"), base / "__init__.py"):
            if path.is_file():
                return path
        return None

    def _dependencies(self, path):
        if path in self.imports:
            return self.imports[path]
        tree = ast.parse(self._source(path), filename=str(path))
        relative = path.relative_to(self.root)
        package = list(relative.parts[:-1])
        targets, uncertain = set(), False
        dynamic_names = {"__import__", "eval", "exec"}
        loader_names = {"import_module", "spec_from_file_location", "SourceFileLoader", "run_path"}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in loader_names:
                        dynamic_names.add(alias.asname or alias.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    if node.level > len(package):
                        uncertain = True
                        continue
                    parts = package[:len(package)-node.level+1]
                    base = ".".join(parts + ([node.module] if node.module else []))
                else:
                    base = node.module or ""
                targets.add(base)
                # A from-import may name a submodule or an ordinary attribute.
                targets.update(base+"."+alias.name for alias in node.names
                               if self._module_path(base+"."+alias.name) is not None)
            elif isinstance(node, ast.Call):
                if ((isinstance(node.func, ast.Name) and node.func.id in dynamic_names)
                        or (isinstance(node.func, ast.Attribute) and node.func.attr in loader_names)):
                    uncertain = True
        dependencies = set()
        for target in targets:
            if target.split(".")[0] not in self.packages:
                continue
            target_path = self._module_path(target)
            if target_path is not None:
                dependencies.add(target_path)
            elif not self.root.joinpath(*target.split(".")).is_dir():
                uncertain = True
        self.imports[path] = dependencies, uncertain
        return dependencies, uncertain

    def identity(self, modules):
        driver = self.root / "scripts/evaluate_joint_extensions.py"
        paths, pending = {driver}, []
        for module in (*_COMMON_RESPONSE_MODULES, *modules):
            path = self._module_path(module)
            if path is None:
                raise ValueError(f"response entry module is missing: {module}")
            pending.append(path)
        # Initializers execute when a package is imported, even if the module
        # itself contains no imports. Namespace packages have no such source.
        def include_initializers(path):
            for parent in path.relative_to(self.root).parents:
                if parent == Path("."):
                    continue
                initializer = self.root / parent / "__init__.py"
                if initializer.is_file() and initializer not in paths:
                    pending.append(initializer)
        include_initializers(driver)
        while pending:
            path = pending.pop()
            if path in paths:
                continue
            paths.add(path)
            include_initializers(path)
            dependencies, uncertain = self._dependencies(path)
            if uncertain:
                paths.update(p for folder in self.packages for p in (self.root/folder).rglob("*.py"))
                break
            pending.extend(dependencies - paths)
        for path in paths:
            self._source(path)
        return {path.relative_to(self.root).as_posix(): self.digests[path] for path in sorted(paths)}


def response_source_identities():
    """Current response-specific source hashes, sharing one import-graph snapshot."""
    graph = _ResponseSourceGraph(ROOT)
    return {name: graph.identity(_RESPONSE_MODULES[name]) for name in RESPONSE_NAMES}


def response_calculation_sources(name):
    """Source identity for one named response, including its shared interfaces."""
    if name not in _RESPONSE_MODULES:
        raise ValueError(f"unknown response: {name}")
    return _ResponseSourceGraph(ROOT).identity(_RESPONSE_MODULES[name])


def calculation_sources():
    """Calculation identity independent of documentation and presentation scripts."""
    paths = [p for folder in ("cg_core", "cg_frg") for p in (ROOT / folder).rglob("*.py")]
    paths.append(Path(__file__).resolve())
    paths.extend(ROOT / p for p in ('comparison/sm_rge/inputs.py',
                                   'scripts/validate_endpoint_cosmology.py'))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def response_bundle(records):
    """Read the unified response records for reports, resolving parameter projections."""
    result = {name: resolve_value(records["response_"+name]["value"], records)
              for name in RESPONSE_NAMES if "response_"+name in records}
    result.update(records.get("response_validation", {}).get("value", {}))
    return result


def _canonical_payload(name, value):
    """Shared tensor coefficients remain projections of their production records."""
    if name != "external_gauge_tensor":
        return value
    result = dict(value)
    for field, key in (("kinetic_GeV_squared", "external_tensor_Z"),
                       ("residue_GeV_inverse_squared", "external_tensor_residue"),
                       ("newton_GeV_inverse_squared", "external_tensor_G")):
        result[field] = {"$ref": key}
    result["ladder_matching"] = dict(value["ladder_matching"])
    for field, key in (("chi_at_zero", "chi_pole_crossing"),
                       ("Pi_at_critical_point", "external_tensor_Pi_critical"),
                       ("minus_dchi_dq_squared", "external_tensor_chi_slope")):
        result["ladder_matching"][field] = {"$ref": key}
    return result


def evaluate(path, *, publish=False, reuse=True):
    from cg_core.params import read_store_document
    from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN
    if path.resolve() != (store_root()/"cg_params.json").resolve():
        raise ValueError("evaluation source must be the configured unified store")
    source = path.read_bytes()
    raw_records = read_store_document()["parameters"]
    ids = {r.get("run_id") for key, r in raw_records.items()
           if r.get("provenance") == "DERIVED" and not key.startswith("response_")}
    if len(ids) != 1 or None in ids:
        raise ValueError("extension requires one fully identified computational run")
    run_id = next(iter(ids))
    if publish and path.resolve() != (store_root()/"cg_params.json").resolve():
        raise ValueError("publication destination must be the configured unified store")
    records = PredictionRecords(raw_records)
    sources = calculation_sources()
    response_sources = response_source_identities()
    cache = {}
    cache_run = None
    reference = Path(os.environ.get("V5_REFERENCE_DIR", str(ROOT))) / "cg_params.json"
    manifest_path = reference.parent / "run_manifest.json"
    if reuse and reference.is_file() and manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest.get("status") == "complete computational run" and manifest.get("run_id")
                and manifest.get("output_sha256", {}).get("cg_params.json") == hashlib.sha256(reference.read_bytes()).hexdigest()):
            cache = read_store_document(source_root=reference.parent)["parameters"]
            cache_run = manifest["run_id"]
    work = {"computed": [], "reused": []}
    def evaluate_one(name, calculate):
        key = "response_"+name
        previous = cache.get(key, {})
        saved = previous.get("calculation", {})
        comparison_inputs = joint_comparison_input_fingerprints() if name == 'joint_response' else {}
        direct = previous.get("direct_inputs")
        reusable = (reuse and previous.get("run_id") == cache_run and saved.get("run_id")
                    and saved.get("source_sha256") == response_sources[name]
                    and saved.get('comparison_input_sha256', {}) == comparison_inputs
                    and isinstance(direct, dict) and "value" in previous)
        if reusable:
            reusable = all(parent in raw_records and value_fingerprint(
                records[parent]["value"]) == digest for parent, digest in direct.items())
        with input_scope() as reads:
            if reusable:
                for parent in direct:
                    records[parent]
                result = resolve_value(previous["value"], raw_records)
                calculation = saved
                work["reused"].append(name)
            else:
                result = calculate()
                calculation = {"run_id": run_id, "source_sha256": response_sources[name],
                               "comparison_input_sha256": comparison_inputs}
                work["computed"].append(name)
            if publish:
                record(key, _canonical_payload(name, result), role="comparison",
                       note="Evaluated response under its explicit operator, source, normalization and approximation; comparison-only diagnostic.",
                       dependencies=tuple(reads),
                       evidence_kind="structured response and its numerical or exact verification",
                       calculation=calculation)
            return result
    with prediction_inputs_only():
        matter = evaluate_one("matter_extensions", lambda: evaluate_matter_extensions(records))
    # The joint check compares already computed readouts, including propagation
    # comparisons. All other evaluations enforce the prediction-only boundary.
    def joint_comparisons():
        result = joint(records)
        # Bind the already evaluated lepton kernel to its actual generation inputs.
        for key in ('m_e_pred', 'm_mu_pred', 'm_tau_pred', 'v_HIGGS',
                    'm_H_pred', 'M_Z_pred', 's2_thetaW_MZ'):
            records[key]
        result['running_mass_comparison'] = published_running_mass_benchmark(
            matter['electroweak_finite_matching']['generated_charged_lepton_realization'])
        result['neutron_helium_comparison'] = neutron_helium_benchmark(
            {key: records[key]['value'] for key in ('bbn_dm_np', 'bbn_tau_n', 'bbn_Yp')},
            generated_joint_response=records['bbn_joint_response']['value'])
        with prediction_inputs_only():
            result['three_quark_source'] = three_quark_source_certificate()
        result['cosmological_mass_scale_comparison'] = registered_scale_diagnostic(
            records['endpoint_camb_record']['value'])
        center = records['endpoint_camb_record']['value']
        if 'thermal_history_budget' in center:
            result['thermal_history_comparison'] = thermal_history_distance_budget(
                center, records['endpoint_bao_record']['value'],
                generated_atomic={'alpha': float(records['alpha_em_0_pred']['value']),
                                  'electron_mass_GeV': float(records['m_e_pred']['value'])/1000})
        return result
    joint_result = evaluate_one("joint_response", joint_comparisons)
    with prediction_inputs_only():
        endpoint = evaluate_one("endpoint_source_response", lambda: evaluate_endpoint_response(
            tau=float(records["tau"]["value"]), response_radius=DEFAULT_RESPONSE_DOMAIN.radius))
        native = evaluate_one("native_operations", evaluate_native_operations)
        matter_source = evaluate_one("finite_matter_source", evaluate_matter_source_response)
        propagated = evaluate_one("neutrino_propagation", lambda: propagation_example(records))
        local = evaluate_one("local_static_response", local_example)
        def feedback_calculation():
            result = local_feedback_example()
            vacuum_fraction = float(records['Omega_Lambda']['value'])
            result['expanding_window'] = evaluate_expanding_rms_window(
                omega_m=1-vacuum_fraction, omega_vacuum=vacuum_fraction,
                acceleration_ratio=float(records['a0_MOND']['value']) / (
                    C_MS*float(records['H0_GEV']['value'])*GEV_TO_S))
            result['passed'] = result['passed'] and result['expanding_window']['passed']
            clock = evaluate_covariant_clock()
            clock_passed = all(row['max_abs_p_error'] < 1e-9 and
                              row['max_abs_foliation_clock_error'] < 1e-10
                              for row in clock['analytic_solution_checks']) and (
                clock['equal_effective_source_comparison']['max_abs_effective_density_difference'] < 1e-9)
            clock_passed = clock_passed and (
                clock['accelerated_static_kinetics']['maximum_identity_residual'] < 1e-12)
            if not clock_passed:
                raise ArithmeticError('covariant clock evolution failed its exact solution checks')
            clock['verification'] = {
                'consistency_checks_passed': clock_passed,
                'scope': 'algebraic reduction and finite evolution of the independent-foliation effective action',
                'kinetic_sign_scope': 'dust-vacuum and accelerated static branches evaluated separately',
            }
            result['covariant_clock'] = clock
            return result
        feedback = evaluate_one("local_source_feedback", feedback_calculation)
        def bandwidth_calculation():
            tau = float(records['tau']['value'])
            result = evaluate_bandwidth_response(tau=tau)
            result['hierarchy_selection'] = evaluate_hierarchy_selection(tau=tau)
            result['passed'] = result['passed'] and result['hierarchy_selection']['passed']
            return result
        bandwidth = evaluate_one("bandwidth_response", bandwidth_calculation)
        free = evaluate_one("free_covariance", free_carrier_checks)
        completed_mixing = evaluate_one("complex_mixing", lambda: mixing(records))
        affine = evaluate_one("exact_affine_certificates", exact_affine_examples)
        undeformed = evaluate_one("undeformed_branch_margin", lambda: undeformed_branch_check(records))
        tensor = evaluate_one("external_gauge_tensor", lambda: external_tensor(records))
        intensity = evaluate_one("native_scalar_intensity", lambda: native_intensity_example(records))
    checks = {"shared_inputs": joint_result["passed"], "endpoint_feedback": endpoint["passed"],
              "native_operations": native["all_checks_passed"],
              "matter_extensions": matter["checks_passed"],
              "finite_matter_source": matter_source["checks_passed"],
              "labelled_propagation": propagated["passed"], "local_response": local["passed"],
              "local_source_feedback": feedback["passed"],
              "independent_foliation_consistency": feedback["covariant_clock"]["verification"]["consistency_checks_passed"],
              "joint_bandwidth_response": bandwidth["passed"],
              "finite_free_covariance": free["free_reflection_gram_min"] >= -1e-12
                  and free["phase_state_min"] >= -1e-12 and free["phase_trace_error"] < 1e-12,
              "exact_affine_certificates": affine["passed"],
              "undeformed_branch_margin": undeformed["passed"],
              "external_gauge_tensor": tensor["passed"],
              "native_scalar_intensity": intensity["passed"],
              "labelled_mixing": completed_mixing["ckm_unitarity_residual"] < 1e-12
                  and completed_mixing["pmns_unitarity_residual"] < 1e-12
                  and completed_mixing["takagi_residual_eV"] < 1e-12}
    if not all(checks.values()):
        raise RuntimeError(f"extension checks failed: {checks}")
    if calculation_sources() != sources or response_source_identities() != response_sources:
        raise RuntimeError("calculation source changed during response evaluation")
    if publish:
        from cg_core.params import get
        with input_scope() as reads:
            for name in RESPONSE_NAMES:
                get("response_"+name)
            record("response_validation", {"checks": checks, "all_checks_passed": True},
                   role="informational", note="Checks of the unified response records in this run.",
                   dependencies=tuple("response_"+name for name in RESPONSE_NAMES))
        print(json.dumps({"response_evaluations": work}, ensure_ascii=False))
    return {"publication": publication_metadata(),
            "run_id": ids.pop(), "input_sha256": hashlib.sha256(source).hexdigest(),
            "evaluation_work": work,
            "scope": "current framework readouts and separately specified conditional operator calculations",
            "complex_mixing": completed_mixing, "joint_response": joint_result,
            "native_operations": native, "endpoint_source_response": endpoint,
            "free_covariance": free, "matter_extensions": matter,
            "finite_matter_source": matter_source,
            "exact_affine_certificates": affine, "undeformed_branch_margin": undeformed,
            "external_gauge_tensor": tensor,
            "native_scalar_intensity": intensity,
            "bandwidth_response": bandwidth, "local_source_feedback": feedback,
            "neutrino_propagation": propagated, "local_static_response": local,
            "checks": checks, "all_checks_passed": all(checks.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=store_root()/"cg_params.json")
    parser.add_argument("--publish", action="store_true", help="publish through the unified parameter interface")
    parser.add_argument("--recompute", action="store_true", help="independently recompute every response")
    args = parser.parse_args()
    result = evaluate(args.store, publish=args.publish, reuse=not args.recompute)
    if args.publish:
        return
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    print(text)


if __name__ == "__main__":
    main()
