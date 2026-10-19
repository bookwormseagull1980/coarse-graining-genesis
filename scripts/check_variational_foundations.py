"""Evaluate the three action-matching calculations without changing stores.

Run from the repository root.  The report contains computed results and
identifies each comparison functional; it does not promote a kernel
normalization to an action stationary equation.
"""
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.ec_variation import (  # noqa: E402
    full_carrier_response, minimal_spin_connection_vertex,
    neutral_connector_schur, production_torsion_variation,
    production_torsion_sector_contract,
    minimal_classical_stationarity, minimal_torsion_spectral_terms,
)
from cg_frg.frg.endpoint_variation import (  # noqa: E402
    survival_stationary_geometry, gaussian_mode_action_derivative,
    four_dimensional_loop_measure,
)
from cg_frg.gauge.zero_mode_reduction import (  # noqa: E402
    required_seven_dimensional_coefficient,
)
from cg_core.connection_action import (  # noqa: E402
    production_curvature_matching, paired_dirac_determinants, minimal_algebraic_torsion_span,
)


def evaluate():
    import numpy as np
    carrier = full_carrier_response()
    spin = minimal_spin_connection_vertex()
    schur = neutral_connector_schur()
    return {
        "complete_carrier": carrier,
        "minimal_neutral_spin_vertex_norm": float(np.linalg.norm(spin["neutral_vertex"])),
        "unit_connector_neutral_coupling_norm": schur["neutral_coupling_norm"],
        "unit_connector_schur_feedback_norm": schur["schur_feedback_norm"],
        "schur_resolvent_residual": float(np.linalg.norm(schur["resolvent_difference"])),
        "homogeneous_production_action_variation": production_torsion_variation(),
        "minimal_coupled_classical_stationarity": minimal_classical_stationarity(),
        "complete_connection_action_matching": production_curvature_matching(),
        "minimal_algebraic_action_span": minimal_algebraic_torsion_span(),
        "two_sign_dirac_determinant_comparison": paired_dirac_determinants(
            Fraction(4), Fraction(3, 2), carrier["gauge_conditioned_tau"], Fraction(1)),
        "minimal_dirac_square_comparison": [
            minimal_torsion_spectral_terms(n, float(carrier["gauge_conditioned_tau"]), 1.)
            for n in (0, 1)
        ],
        "torsion_sector_transfer_at_unit_radius": production_torsion_sector_contract(
            float(carrier["gauge_conditioned_tau"]), 1.),
        "survival_profile": survival_stationary_geometry(),
        "gaussian_logdet_derivative_at_profile_maximum": gaussian_mode_action_derivative(Fraction(1, 3), Fraction(1)),
        "four_dimensional_loop_measure": four_dimensional_loop_measure(),
        "gauge_action_matching": {
            "identity": "g7^2 = 8*pi^2/(M_P^2*M_G)",
            "meaning": "coefficient required to reproduce the V5 prescription",
            "unit_comparison": required_seven_dimensional_coefficient(1., 1., 2.),
            "production_scale_provenance": "SCALE_CHOICE",
        },
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, ensure_ascii=False,
                     default=lambda value: str(value) if isinstance(value, Fraction) else value))
