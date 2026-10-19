"""Gauge zero-mode action matching and the registered V5 scale convention.

For S7=1/(4g7^2) int F^2, A_mu(x,y)=a_mu(x) psi0(y), the same
connection/charge convention gives 1/g4^2=int|psi0|^2/g7^2.  A normalized
constant eigenfunction and a constant connection coordinate are different
coordinates: their charged vertex must be transformed at the same time.
"""
import math


def _positive(**values):
    if any(not math.isfinite(value) or value <= 0 for value in values.values()):
        raise ValueError("finite positive values required: " + ", ".join(values))


def zero_mode_action(radius, g7_squared, mode_amplitude=1.0):
    """Exact round RP3 volume integral for the constant gauge mode.

    g7^2 has mass dimension -3 and radius has dimension -1.  A fixed
    connection uses psi0=1.  The L2-normalized psi0=V^-1/2 instead
    changes the zero-mode coordinate and its charged vertex.
    """
    _positive(radius=radius, g7_squared=g7_squared)
    if not math.isfinite(mode_amplitude) or mode_amplitude == 0:
        raise ValueError("a finite nonzero zero-mode amplitude is required")
    volume = math.pi**2*radius**3
    overlap = volume*mode_amplitude**2
    return {"volume": volume, "zero_mode_overlap": overlap,
            "inverse_g4_squared": overlap/g7_squared,
            "quadratic_action_coefficient": overlap/(4*g7_squared),
            "charged_vertex_before_canonical_normalization": mode_amplitude,
            "charge_normalized_g4_squared": mode_amplitude**2/(overlap/g7_squared)}


def gauge_scale_factor(m_g, m_p):
    """The production prescription (M_G/M_P)^2, not an added fit input."""
    _positive(m_g=m_g, m_p=m_p)
    return (m_g/m_p)**2


def killing_coupling_squared(m_g, m_p, k_l):
    _positive(k_l=k_l)
    return 8*gauge_scale_factor(m_g, m_p)/k_l**3


def required_seven_dimensional_coefficient(m_g, m_p, k_l):
    """Compute the g7^2 needed to match V5, not a derivation of that g7^2.

    With physical radius R=kL/M_G, V=pi^2 R^3 and g4^2=8(M_G/M_P)^2/kL^3,
    the exact matching condition is g7^2=8*pi^2/(M_P^2*M_G).
    Both the unreduced integral and the simplified expression are returned.
    """
    _positive(m_g=m_g, m_p=m_p, k_l=k_l)
    radius = k_l/m_g
    g4_squared = killing_coupling_squared(m_g, m_p, k_l)
    volume = math.pi**2*radius**3
    return {"radius": radius, "volume": volume, "g4_squared": g4_squared,
            "g7_squared_required": volume*g4_squared,
            "g7_squared_simplified": 8*math.pi**2/(m_p**2*m_g)}


def register_gauge_scale_factor():
    """Publish the prescription and exact store parents before using it."""
    from cg_core.params import get, set as pset
    m_g, m_p = float(get("M_G")), float(get("M_P"))
    value = gauge_scale_factor(m_g, m_p)
    pset("gauge_kinetic_scale_factor", value, provenance="SCALE_CHOICE",
         dependencies=("M_G", "M_P"),
         evidence_kind="evaluated registered normalization prescription",
         note="Killing-response prescription (M_G/M_P)^2; a 7D action matching "
              "would require g7^2=8*pi^2/(M_P^2*M_G), which is not inferred "
              "from the constant-mode overlap alone")
    return float(get("gauge_kinetic_scale_factor"))
