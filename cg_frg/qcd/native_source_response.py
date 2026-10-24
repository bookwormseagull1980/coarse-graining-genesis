"""Publish the native intensity and complete curvature source response."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.native_colour_response import colour_source_response
from cg_core.params import get, set as pset
from cg_core.quantities import QuantityDefinition


def compute():
    response = colour_source_response(get("generated_ym_mass_gap"))
    pset("native_colour_source_response", response, provenance="DERIVED", role="internal",
         dependencies=("generated_ym_mass_gap",),
         definition=QuantityDefinition(
             object="native intensity composition, complete colour-curvature memory and joint static susceptibility",
             unit="native source units", carrier="15 coexact spatial modes times 8 colour components",
             operator="coefficient Mehler composition, Q=||dB+B wedge B||^2 and the stationary joint-source Schur response",
             source="generated_ym_mass_gap", projection="Hermite degrees 2, 3 and 4 with all spatial contractions",
             normalization="original Haar volume and coefficient Gaussian variance q/120",
             scheme="native three-dimensional finite source; Phi(n,J)=F(n)+Gamma(n,J)-Gamma(n,0)", order="complete quartic curvature observable and static linear response",
             assumptions=("same coefficient source and equilibrium composition as the generated operator",),
             error_kind="finite algebraic formulas evaluated in binary floating point; no lepton matching error assigned"),
         note="No radial replacement, new variance, clock conversion or fitted mass vertex.")
    return response


if __name__ == "__main__":
    print(compute())
