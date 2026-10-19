"""Evaluate and certify the action-consistent finite-window torsion saddle.

The default calculation holds the stored TT endpoint kL fixed. With
--joint-radius-bracket LMIN LMAX, solve the two variations of the
trace-matched curvature/fermion action and certify a local Newton box.
Both modes write reports to stdout rather than change parameter stores.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cg_core.params import get
from cg_core.release import publication_metadata
from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN
from cg_frg.ewsb.torsion_response import solve_torsion_window
from cg_frg.ewsb.torsion_geometry import (
    trace_matched_curvature_response, solve_joint_window_saddle,
    certify_joint_window_saddle,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=float, help="fixed dimensionless radius; default: stored kL")
    parser.add_argument("--joint-radius-bracket", type=float, nargs=2, metavar=("LMIN", "LMAX"),
                        help="joint radius/torsion solution in one spectral chamber")
    parser.add_argument("--cells", type=int, default=512, help="outward frequency partition")
    args = parser.parse_args()
    if args.joint_radius_bracket is not None:
        if args.radius is not None:
            parser.error("--radius and --joint-radius-bracket select different calculations")
        result = solve_joint_window_saddle(radius_bracket=args.joint_radius_bracket, scale=1.)
        tau, radius = result["tau_estimate"], result["radius_estimate"]
        result["local_joint_certificate"] = certify_joint_window_saddle(
            tau_interval=(max(-.499, tau-.005), min(.249, tau+.005)),
            radius_interval=(max(args.joint_radius_bracket[0], radius-.005),
                             min(args.joint_radius_bracket[1], radius+.005)),
            center=(tau, radius), scale=1., cells=args.cells)
        certified = result["local_joint_certificate"]["unique_joint_stationary_point_certified"]
        result["interval_existence_or_uniqueness_certificate"] = certified
        if certified:
            result["status"] = "certified locally unique stationary point of the specified common action"
    else:
        radius = get("kL") if args.radius is None else args.radius
        result = solve_torsion_window(radius=radius, scale=1.,
                                      domain=DEFAULT_RESPONSE_DOMAIN, cells=args.cells)
        if "root_estimate" in result:
            geometry = trace_matched_curvature_response(result["root_estimate"], radius=radius, scale=1.)
            result["radius_equation_at_fixed_radius_torsion_saddle"] = {
                "integrated_gradient": geometry["curvature_completed"]["integrated_gradient"],
                "reference_radius_force": geometry["reference"]["integrated_gradient"][1],
                "frequency_boundary_radius_force": geometry["full"]["integrated_radius_boundary"],
                "scope": geometry["scope"],
            }
    print(json.dumps({"publication": publication_metadata(), **result}, indent=2))


if __name__ == "__main__":
    main()
