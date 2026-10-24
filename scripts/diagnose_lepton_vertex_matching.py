"""Read-only action-level diagnostic for the charged-lepton mass invariant.

Run: python scripts/diagnose_lepton_vertex_matching.py --compare-reference
The optional comparison runs after the generated calculation has completed.
No parameter store, release manifest or production output is written.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.matter_matching import charged_lepton_pole_matching_one_loop
from cg_core.native_matter_matching import radial_spinor_family
from cg_core.params import get, input_scope, prediction_inputs_only
from cg_frg.fermion.lepton_pole import lepton_mass_vertex_response
from cg_frg.fermion.lepton_self_energy import charged_lepton_chiral_self_energy_one_loop
from cg_frg.fermion.native_source_attachment import native_lepton_attachment
from cg_core.native_colour_response import colour_source_response


def native_frame_transport_diagnostic(masses_GeV, *, basepoint=(.23, -.31, .19)):
    """Check the finite source kernel with its original complement retained.

    The basepoint is a deterministic coordinate check, not a random variable
    assigned the colour source law. Transfer weights are held fixed. The
    mass-squared resolvent below is that of the finite internal vertex; it is
    not identified with the interacting spacetime fermion propagator.

    Freezing the original radial subspace while moving the kernel can change
    the compressed singular values. Exact elimination of its complement
    retains the original nonzero spectral positions. Thus a change of source
    presentation is not by itself a finite quantum matching coefficient.
    """
    masses = np.asarray(masses_GeV, float)
    if (masses.shape != (3,) or not np.isfinite(masses).all()
            or np.any(masses <= 0) or np.any(np.diff(masses) <= 0)):
        raise ValueError("three positive increasing lepton masses required")
    original = radial_spinor_family()
    moved = radial_spinor_family(basepoint=basepoint)
    r0, r = original["embedding"], moved["embedding"]
    small = np.diag(np.repeat(masses, 2))
    vertex = r @ small @ r.conj().T
    transported = r.conj().T @ vertex @ r
    full_values = np.linalg.svd(vertex, compute_uv=False)[:6][::-1]

    fixed = r0.conj().T @ vertex @ r0
    fixed_family = np.array([[np.trace(fixed[2*i:2*i+2, 2*j:2*j+2])/2
                              for j in range(3)] for i in range(3)])
    # Do not assume a scalar spin factor after freezing the old subspace.
    fixed_spin_error = np.linalg.norm(fixed-np.kron(fixed_family, np.eye(2)), ord=2)
    fixed_values = np.linalg.svd(fixed_family, compute_uv=False)[::-1]
    weighted_log = lambda x: math.fsum(w*math.log(float(a)) for w, a in
                                      zip((-1, 2, -1), x))

    # Preserve the existing shell blocks when completing the basis, so a
    # heavy-family roundoff error is not magnified at the electron position.
    complements = []
    for i, shell in enumerate(original["family_shell_order"]):
        rows = [a for a, label in enumerate(original["labels"]) if label[0] == shell]
        local = np.linalg.qr(r0[rows, 2*i:2*i+2], mode="complete")[0][:, 2:]
        block = np.zeros((len(r0), local.shape[1]), complex)
        block[rows, :] = local
        complements.append(block)
    q0 = np.column_stack(complements)
    h = vertex.conj().T @ vertex
    hss, hsq, hqq = r0.conj().T@h@r0, r0.conj().T@h@q0, q0.conj().T@h@q0
    hs = hsq.conj().T

    def schur(z):
        return z*np.eye(6)-hss-hsq@np.linalg.solve(z*np.eye(len(q0.T))-hqq, hs)

    z = -masses[1]**2
    projected_resolvent = r0.conj().T @ np.linalg.solve(z*np.eye(len(h))-h, r0)
    schur_resolvent = np.linalg.inv(schur(z))
    poles = []
    for i, mass in enumerate(masses):
        retained_eigenvectors = r0.conj().T @ r[:, 2*i:2*i+2]
        pole_residual = np.linalg.norm(schur(mass**2) @ retained_eigenvectors, ord=2)
        poles.append(float(pole_residual/(mass**2*np.linalg.norm(retained_eigenvectors, ord=2))))
    return {
        "basepoint": np.asarray(basepoint, float).tolist(),
        "ambient_dimension": len(h), "retained_dimension": 6,
        "full_mass_relative_residual": float(np.max(abs(full_values/np.repeat(masses, 2)-1))),
        "transported_vertex_relative_residual": float(np.linalg.norm(transported-small, ord=2)/masses[-1]),
        "fixed_subspace_masses_GeV": fixed_values.tolist(),
        "fixed_subspace_spin_factorization_residual_GeV": float(fixed_spin_error),
        "fixed_subspace_apparent_log_shift": weighted_log(fixed_values)-weighted_log(masses),
        "complement_feedback_norm_GeV2": float(np.linalg.norm(hsq, ord=2)),
        "schur_projected_resolvent_relative_residual": float(
            np.linalg.norm(schur_resolvent-projected_resolvent, ord=2)
            / np.linalg.norm(projected_resolvent, ord=2)),
        "schur_nonzero_spectral_position_relative_residuals": poles,
        "transfer_weights_changed": False,
        "generated_source_loop_correction_computed": False,
        "scope": "exact finite vertex transport and complement elimination; no spacetime self-energy assigned",
    }


def evaluate_lepton_vertex_diagnostic():
    """Evaluate the radial source, D and the common-action chiral diagrams.

    The unit variations are derivatives of common normalization directions,
    not proposed radiative corrections. The tree operator uses the existing
    generated masses, without independently deriving their transfer weights.
    """
    with prediction_inputs_only(), input_scope() as reads:
        masses = np.array([float(get("m_e_pred")) / 1000,
                           float(get("m_mu_pred")), float(get("m_tau_pred"))])
        vev, scale, higgs = (float(get(key)) for key in
                             ("v_HIGGS", "M_Z_pred", "m_H_pred"))
        weak_fraction = float(get("s2_thetaW_MZ"))
        complete_colour_response = colour_source_response(get("generated_ym_mass_gap"))
        if not 0 < weak_fraction < 1:
            raise ValueError("generated weak fraction must lie between zero and one")
        gauge_sum = 4 * scale**2 / vev**2
        gauge = [math.sqrt(5 * weak_fraction * gauge_sum / 3),
                 math.sqrt((1 - weak_fraction) * gauge_sum)]
        radial = radial_spinor_family()
        embedding = radial["embedding"]
        operator = sum(mass * p for mass, p in zip(masses, radial["projectors"]))
        small = embedding.conj().T @ operator @ embedding
        vertex = np.array([[np.trace(small[2*i:2*i+2, 2*j:2*j+2]) / 2
                            for j in range(3)] for i in range(3)])
        identity, zero = np.eye(3), np.zeros((3, 3))
        source = "existing V5 radial family mass vertex and inherited Haar kinetic norm"
        directions = {}
        for name, (db, dl, dr) in {
            "common_vertex": (vertex, zero, zero),
            "common_left_kinetic": (zero, identity, zero),
            "common_right_kinetic": (zero, zero, identity),
        }.items():
            response = lepton_mass_vertex_response(
                vertex, identity, identity, delta_mass_vertex_GeV=db,
                delta_left_gram=dl, delta_right_gram=dr, action_source=source)
            directions[name] = {"dlog_masses": response["dlog_masses"],
                                "weighted_log_response": response["weighted_log_response"]}
        family_directions = {}
        for i, name in enumerate(("light", "middle", "heavy")):
            # Differentiate the actual source projector, not a fitted mass.
            small_delta = embedding.conj().T @ (radial["projectors"][i] @ operator) @ embedding
            delta_vertex = np.array([[np.trace(small_delta[2*j:2*j+2, 2*k:2*k+2]) / 2
                                      for k in range(3)] for j in range(3)])
            response = lepton_mass_vertex_response(
                vertex, identity, identity, delta_mass_vertex_GeV=delta_vertex,
                delta_left_gram=zero, delta_right_gram=zero, action_source=source)
            family_directions[name] = response["weighted_log_response"]
        # With the heavy normalization held fixed, m=(A*exp(-4a-L),
        # A*exp(-2a), A). Holding the electron anchor instead changes these
        # derivatives by a common direction, whose weighted response is zero.
        transfer_directions = {}
        for name, coefficients in {"common_rung_alpha": (-4., -2., 0.),
                                    "light_period": (-1., 0., 0.)}.items():
            delta_operator = sum(c * m * p for c, m, p in
                                 zip(coefficients, masses, radial["projectors"]))
            small_delta = embedding.conj().T @ delta_operator @ embedding
            delta_vertex = np.array([[np.trace(small_delta[2*j:2*j+2, 2*k:2*k+2]) / 2
                                      for k in range(3)] for j in range(3)])
            response = lepton_mass_vertex_response(
                vertex, identity, identity, delta_mass_vertex_GeV=delta_vertex,
                delta_left_gram=zero, delta_right_gram=zero, action_source=source)
            transfer_directions[name] = {"dlog_masses": response["dlog_masses"],
                                         "weighted_log_response": response["weighted_log_response"]}
        complement = np.eye(len(embedding)) - radial["source_projector"]
        kernel = charged_lepton_pole_matching_one_loop(
            dict(zip(("electron", "muon", "tau"), masses)), gauge, vev,
            higgs_mass_GeV=higgs, scale_GeV=scale,
            input_definition="generated_on_shell_conditions",
            action_source="existing generated leading weak inputs; zeroth-order geometric mass arguments")
        action_source = "existing generated leading weak inputs; canonical local lepton action"
        common_args = dict(higgs_mass_GeV=higgs, scale_GeV=scale, action_source=action_source)
        mass_arguments = dict(zip(("electron", "muon", "tau"), masses))
        pole_two_point = charged_lepton_chiral_self_energy_one_loop(
            mass_arguments, gauge, vev, **common_args)
        spacelike_two_point = charged_lepton_chiral_self_energy_one_loop(
            mass_arguments, gauge, vev,
            momentum_squared_GeV2={name: -scale**2 for name in mass_arguments}, **common_args)
        subtraction_terms = {}
        for name, value in spacelike_two_point["species"].items():
            total = value["total"]
            subtraction_terms[name] = {key: total[key]["real"] for key in
                                      ("delta_mass_vertex_GeV", "delta_left_kinetic", "delta_right_kinetic")}
        log_invariant = math.fsum(w * math.log(m) for w, m in zip((-1, 2, -1), masses))
        result = {
            "geometric_masses_GeV": dict(zip(("e", "mu", "tau"), map(float, masses))),
            "geometric_log_invariant": log_invariant,
            "geometric_period": math.sqrt(2 * math.pi),
            "geometric_identity_residual": log_invariant - math.sqrt(2 * math.pi),
            "native_source": {
                "ambient_dimension": len(embedding), "radial_dimension": embedding.shape[1],
                "canonical_mass_singular_values_GeV": np.linalg.svd(vertex, compute_uv=False)[::-1].tolist(),
                "spin_factorization_residual": float(np.linalg.norm(small - np.kron(vertex, np.eye(2)), ord=2)),
                "complement_mass_vertex_norm_GeV": float(np.linalg.norm(operator @ complement, ord=2)),
                "scope": "tree mass vertex; zero complement block does not exclude interaction-mediated thresholds",
            },
            "native_frame_transport": native_frame_transport_diagnostic(masses),
            "native_colour_source_response": complete_colour_response,
            "native_lepton_source_attachment": native_lepton_attachment(),
            "common_normalization_directions": directions,
            "family_projector_weighted_sensitivities": family_directions,
            "lepton_transfer_directions": transfer_directions,
            "normalization_and_projector_directions_are_loop_coefficients": False,
            "pole_to_MSbar": {
                "scale_GeV": scale, "gauge_couplings_GUT_g1_g2": gauge,
                "Delta_D_first_order": kernel["charged_lepton_log_correction"],
                "Delta_D_numerical_interval": kernel["charged_lepton_log_correction_interval"],
                "weighted_log_components": kernel["weighted_log_components"],
                "photon_log_invariant_identity_residual": (
                    kernel["weighted_log_components"]["photon"]
                    - 3 * kernel["alpha_same_action"] * log_invariant / (2 * math.pi)),
                "weighted_log_scale_derivative": kernel["weighted_one_loop_log_scale_derivative"],
                "scope": "one-loop EFT kernel at zeroth-order generated masses; finite vertex matching separate",
            },
            "matching_equation_first_order": "Delta_pole = Delta_C - Delta_D",
            "common_action_two_point": {
                "on_shell": pole_two_point,
                "spacelike_momentum_squared_GeV2": -scale**2,
                "spacelike_shared_terms_to_subtract": subtraction_terms,
                "on_shell_recombination_residual": (
                    pole_two_point["weighted_mass_combination"]["real"]
                    + kernel["charged_lepton_log_correction"]),
                "matching_difference_definition": (
                    "delta B = Omega_gen - Omega_EFT; "
                    "delta K_L/R = -Sigma_gen_L/R + Sigma_EFT_L/R; same action convention and momentum"),
                "shared_graph_cancellation": "identical local graphs cancel before canonical mass response",
                "generated_source_excess_computed": False,
                "spacelike_coefficients_are_LSZ_residues": False,
            },
            "native_matching_terms_required": ["delta_mass_vertex_GeV", "delta_left_kinetic_form",
                                                "delta_right_kinetic_form"],
            "matching_prescription": "same generated/EFT amplitudes and momenta; subtract common EFT loops before applying D",
            "generated_vertex_loop_correction_calculated": False,
            "production_replacement": False,
        }
    result["generated_input_keys"] = sorted(reads)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-reference", action="store_true")
    options = parser.parse_args()
    result = evaluate_lepton_vertex_diagnostic()
    if options.compare_reference:
        from comparison.lepton_vertex_matching import compare_lepton_vertex_matching
        result["comparison"] = compare_lepton_vertex_matching(result)
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
