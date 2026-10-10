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

"""Evaluate the full native condensate for explicitly supplied response data."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cg_core.release import publication_metadata
from cg_frg.ewsb.native_condensate import solve_native_condensate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("g","Z","L"):
        parser.add_argument("--"+key,required=True,help="explicit decimal in declared response units")
    parser.add_argument("--shells",type=int,default=512)
    args=parser.parse_args()
    result = {"publication": publication_metadata(),
              **solve_native_condensate(g=args.g, Z=args.Z, L=args.L, shells=args.shells)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
