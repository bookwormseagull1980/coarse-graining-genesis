"""Evaluate the fixed-content lift and explicit connection comparisons.

The default calculation fixes tau by its exact capacity equation and
evaluates the displayed action at the stored TT endpoint kL. With
--content-radius-bracket LMIN LMAX, vary only its radius and certify a
restricted minimum. With --vary-connection, reproduce the independent
connection variation at fixed radius. With
--joint-radius-bracket LMIN LMAX, solve the two variations of the
trace-matched curvature/fermion action and certify a local Newton box.
All modes write reports to stdout rather than change parameter stores.
"""
import argparse
import json
from fractions import Fraction
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
    content_fixed_geometry_response, solve_content_fixed_radius,
    certify_content_fixed_radius,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=float, help="fixed dimensionless radius; default: stored kL")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--content-radius-bracket", type=float, nargs=2, metavar=("LMIN", "LMAX"),
                       help="radius variation with exact content tau fixed")
    modes.add_argument("--vary-connection", action="store_true",
                       help="comparison: vary an independent connection at fixed radius")
    modes.add_argument("--joint-radius-bracket", type=float, nargs=2, metavar=("LMIN", "LMAX"),
                       help="comparison: joint radius/independent-connection variation")
    parser.add_argument("--cells", type=int, default=512, help="outward frequency partition")
    args = parser.parse_args()
    if args.radius is not None and (args.joint_radius_bracket is not None or
                                    args.content_radius_bracket is not None):
        parser.error("--radius and a radius search bracket select different calculations")
    if args.content_radius_bracket is not None:
        result = solve_content_fixed_radius(radius_bracket=args.content_radius_bracket, scale=1.)
        length = result["radius_estimate"]
        result["local_radius_certificate"] = certify_content_fixed_radius(
            radius_interval=(max(args.content_radius_bracket[0], length-.005),
                             min(args.content_radius_bracket[1], length+.005)),
            scale=1., cells=args.cells)
        certified = result["local_radius_certificate"]["unique_restricted_radius_minimum_certified"]
        result["interval_existence_or_uniqueness_certificate"] = certified
        if certified:
            result["status"] = "certified local radius minimum on the fixed-content lift"
    elif args.joint_radius_bracket is not None:
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
    elif args.vary_connection:
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
    else:
        radius = get("kL") if args.radius is None else args.radius
        data = content_fixed_geometry_response(radius=radius, scale=1.)
        result = {
            "status": "fixed content evaluated on its isotropic connection lift",
            "tau_content_exact": data["tau_content_exact"],
            "tau_content": data["tau_content"], "radius": radius,
            "content_balance": data["content_balance"],
            "content_fixed": data["content_fixed"],
            "scope": data["scope"], "construction": data["construction"],
        }
    print(json.dumps({"publication": publication_metadata(), **result}, indent=2,
                     default=lambda value: str(value) if isinstance(value, Fraction) else value.tolist()))


if __name__ == "__main__":
    main()
