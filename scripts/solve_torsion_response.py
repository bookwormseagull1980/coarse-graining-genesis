"""Evaluate and certify the action-consistent finite-window torsion saddle.

The default radius is the existing V5 TT endpoint stored as kL.  It is
held fixed during this calculation; solving all geometry/Higgs equations
is a different calculation.  Output is written to stdout, so this command
does not replace the published tau or any parameter-store record.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=float, help="fixed dimensionless radius; default: stored kL")
    parser.add_argument("--cells", type=int, default=512, help="outward frequency partition")
    args = parser.parse_args()
    radius = get("kL") if args.radius is None else args.radius
    result = solve_torsion_window(radius=radius, scale=1.,
                                  domain=DEFAULT_RESPONSE_DOMAIN, cells=args.cells)
    print(json.dumps({"publication": publication_metadata(), **result}, indent=2))


if __name__ == "__main__":
    main()
