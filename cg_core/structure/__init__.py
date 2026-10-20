# -*- coding: utf-8 -*-
"""Structural closure certificates for V5.

This package starts from the minimal unbiased compositional change datum and
derives the structural facts used by the numerical chain.  It is deliberately
independent of the Lean physical branch: the certificates are finite, exact
or interval-checked statements computed inside V5.

The package does not replace a proof assistant.  It records the same
structural steps in executable form so that V5 can reproduce its own
minimal-change -> Gaussian -> internal geometry -> content -> capacity chain.
"""

from .minimal_change import certificate as minimal_change_certificate
from .rp3_derivation import certificate as rp3_derivation_certificate
from .internal_geometry import certificate as internal_geometry_certificate
from .content_capacity import certificate as content_capacity_certificate
from .response_level import certificate as response_level_certificate
from .normalization import certificate as normalization_certificate
from .projection import certificate as projection_certificate
from .matching import certificate as matching_certificate
from .capacity_closure import certificate as capacity_closure_certificate
from cg_core.tt_branch_reduction import certificate as tt_branch_reduction_certificate
import json
from pathlib import Path


_ENDPOINT_CERT = Path(__file__).resolve().parents[2] / "certificates" / "endpoint_interval.json"


def endpoint_interval_cached() -> dict:
    """Load the one-time strict endpoint certificate; never recompute it."""
    if not _ENDPOINT_CERT.is_file():
        raise RuntimeError(
            "missing certificates/endpoint_interval.json; run "
            "py scripts/certify_endpoint_interval.py --cells 2048 once")
    data = json.loads(_ENDPOINT_CERT.read_text(encoding="utf-8"))
    if data.get("status") != "PASS":
        raise RuntimeError("cached endpoint interval certificate is not PASS")
    data["cached"] = True
    return data


def all_certificates() -> dict:
    """Return the V5 structural certificates in dependency order."""
    return {
        "minimal_change": minimal_change_certificate(),
        "rp3_derivation": rp3_derivation_certificate(),
        "internal_geometry": internal_geometry_certificate(),
        "content_capacity": content_capacity_certificate(),
        "response_level": response_level_certificate(),
        "normalization": normalization_certificate(),
        "projection": projection_certificate(),
        "matching": matching_certificate(),
        "capacity_closure": capacity_closure_certificate(),
        "endpoint_interval": endpoint_interval_cached(),
        "tt_branch_reduction": tt_branch_reduction_certificate(),
    }
