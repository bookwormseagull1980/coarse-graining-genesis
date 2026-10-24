# -*- coding: utf-8 -*-
"""Propagate endpoint intervals into the specified production readouts.

The charged leptons and bottom use their complete dependence on the same
endpoint. The Z response reruns its gauge boundary and fixed point; those
numerical samples are not an interval certificate. The separate linear
transfers hold their stated conversion ratios fixed.
"""

from __future__ import annotations

import sys
import math
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import annotate_interval, get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_core.rational_interval import Interval, exp_negative, pi_interval  # noqa: E402


def lepton_endpoint_enclosures(endpoint_interval, *, M_P, tau, ns_tilt):
    """Enclose the production muon/tau formulas on one common endpoint.

    With a=1-12*ns_tilt*(1-tau/4), alpha_lepton=a*c-2*tau and
    m_l=M_P*squash*exp((-20+k*a)*c-2*k*tau+sqrt(2*pi)), k=2,4.
    Combining the exponent before interval evaluation retains the shared c.
    The other generated inputs are fixed at their recorded values. These
    component enclosures are not independent statistical mass errors.
    """
    lo, hi = float(endpoint_interval["lo"]), float(endpoint_interval["hi"])
    M_P, tau, ns_tilt = float(M_P), float(tau), float(ns_tilt)
    if not all(math.isfinite(value) for value in (lo, hi, M_P, tau, ns_tilt)):
        raise ValueError("finite endpoint and generated mass inputs required")
    if not 0 < lo <= hi or M_P <= 0 or not 0 <= tau < .25 or ns_tilt < 0:
        raise ValueError("positive endpoint and Planck scale on the squash branch required")
    # Include possible binary rounding of the stored rational endpoint bounds.
    c = Interval.bounds(math.nextafter(lo, -math.inf), math.nextafter(hi, math.inf))
    t, tilt = Interval.point(tau), Interval.point(ns_tilt)
    s = 2*t
    base = 1-2*s
    kappa = ((1+s)/(base**2*base.sqrt())).sqrt()
    squash = 1-s*kappa
    if squash.lo <= 0:
        raise ValueError("positive squash-corrected mass branch required")
    a = 1-12*tilt*(1-t/4)
    period = (2*pi_interval()).sqrt()
    out = {}
    for name, k in (("m_mu_pred", 2), ("m_tau_pred", 4)):
        exponent = (20-k*a)*c+2*k*t-period
        value = Interval.point(M_P)*squash*exp_negative(exponent)
        exact_bounds = value.decimal_bounds(40)
        out[name] = {
            "lo": math.nextafter(float(exact_bounds[0]), -math.inf),
            "hi": math.nextafter(float(exact_bounds[1]), math.inf),
            "decimal_bounds_GeV": exact_bounds,
        }
    return out


def bottom_endpoint_enclosure(endpoint_interval, *, M_P, tau, ns_tilt):
    """Outward enclosure of v/sqrt(2)*exp(-2*alpha_down+tilt*(c_CMB+2*tau))."""
    # Validate the shared inputs and squash branch using the same mass chain.
    lepton_endpoint_enclosures(endpoint_interval, M_P=M_P, tau=tau, ns_tilt=ns_tilt)
    c = Interval.bounds(math.nextafter(float(endpoint_interval["lo"]), -math.inf),
                        math.nextafter(float(endpoint_interval["hi"]), math.inf))
    t, tilt = Interval.point(float(tau)), Interval.point(float(ns_tilt))
    pi = pi_interval()
    s = 2*t
    squash = 1-s*((1+s)/((1-2*s)**2*(1-2*s).sqrt())).sqrt()
    a_down = 1-Interval.point("108/17")*tilt*(1-t/4)
    exponent = (4*pi+2*a_down-tilt*(1-t/4))*c-4*t-2*t*tilt
    value = (Interval.point(float(M_P))*3*squash
             /(16*pi**2*pi.sqrt()*c*Interval.point(2).sqrt())*exp_negative(exponent))
    exact = value.decimal_bounds(40)
    return {"lo": math.nextafter(float(exact[0]), -math.inf),
            "hi": math.nextafter(float(exact[1]), math.inf),
            "decimal_bounds_GeV": exact}


def z_endpoint_response(endpoint_interval, *, centre, M_P, tau):
    """Recompute the Z fixed point at the two endpoints and centre.

    Includes generated gauge boundaries, common-origin colour shooting,
    emergence scale and VEV. Step-doubling controls the individual numerical
    solves; three samples do not prove a bound between those samples.
    """
    from cg_core.gauge_running import common_origin
    from cg_core.joint_response import evaluate
    from cg_frg.ewsb.ew_precision import mz_fixed_point

    lo, hi = float(endpoint_interval["lo"]), float(endpoint_interval["hi"])
    if not 0 < lo <= centre <= hi:
        raise ValueError("positive endpoint bracket containing the centre required")
    samples = []
    for c in (lo, float(centre), hi):
        p = evaluate(c, float(tau), float(M_P))
        origin = common_origin(p["g1_MG_geo"], p["g2_MG"], p["M_G"], p["k_GUT"])
        value, *_ = mz_fixed_point(p["v_HIGGS"], p["g1_MG_geo"], p["g2_MG"],
                                  origin["g3_initial"], p["M_G"])
        samples.append({"kL": c, "M_Z_GeV": value,
                        "common_origin_relative_residual": origin["relative_residual"]})
    values = [point["M_Z_GeV"] for point in samples]
    return {"samples": samples, "sample_range_GeV": [min(values), max(values)],
            "source": "kL_interval", "certified_enclosure": False,
            "method": "checked two-loop RK4 and self-consistent Z fixed point",
            "error_kind": "sampled endpoint response; integration and unsampled-interior errors separate"}


def right_weak_endpoint_enclosure(endpoint_interval, *, M_P, tau):
    """Enclose g2(c)*(2*tau)*M_G(c), retaining the generated g2 boundary."""
    lepton_endpoint_enclosures(endpoint_interval, M_P=M_P, tau=tau, ns_tilt=0.)
    c = Interval.bounds(math.nextafter(float(endpoint_interval["lo"]), -math.inf),
                        math.nextafter(float(endpoint_interval["hi"]), math.inf))
    pi, t = pi_interval(), Interval.point(float(tau))
    inverse_alpha = c**5/2+Interval.point("1/3")-t**2*pi/2
    if inverse_alpha.lo <= 0:
        raise ValueError("positive generated weak-coupling boundary required")
    value = 4*t*float(M_P)*pi/(c*inverse_alpha.sqrt())
    exact = value.decimal_bounds(40)
    return {"lo": math.nextafter(float(exact[0]), -math.inf),
            "hi": math.nextafter(float(exact[1]), math.inf),
            "decimal_bounds_GeV": exact}


def _lepton_intervals():
    inputs = {key: get(key) for key in ("M_P", "tau", "ns_tilt")}
    bounds = lepton_endpoint_enclosures(get("kL_interval"), **inputs)
    out = {}
    for name, interval in bounds.items():
        centre = float(get(name))
        if not interval["lo"] <= centre <= interval["hi"]:
            raise RuntimeError(f"{name} endpoint interval misses production")
        record = {**interval, "centre": centre, "source": "kL_interval",
                  "relative_width": (interval["hi"]-interval["lo"])/centre}
        output_name = name+"_interval"
        pset(output_name, record, provenance="DERIVED", role="internal",
             dependencies=("kL_interval", "M_P", "tau", "ns_tilt", name),
             definition=QuantityDefinition(
                 object="charged-lepton geometric mass endpoint enclosure", unit="GeV",
                 carrier="same electron cascade and lepton ladder as production",
                 operator="M_P*squash*exp((-20+k*a)*c-2*k*tau+sqrt(2*pi)), k=2,4",
                 source="common kL interval with generated Planck, torsion and tilt inputs",
                 projection=f"same readout as {name}",
                 normalization="GeV; a=1-12*ns_tilt*(1-tau/4)",
                 scheme="outward rational interval propagation of the complete endpoint dependence",
                 order="same geometric mass formula as production",
                 assumptions=("Planck anchor, torsion and tilt held at their generated values",),
                 error_kind="endpoint enclosure; physical matching and anchor errors separate"),
             note="Common endpoint propagated through the electron cascade and both lepton ladder factors.")
        annotate_interval(name, {"lo": interval["lo"], "hi": interval["hi"]},
                          source="kL_interval", note="complete electron-and-ladder endpoint propagation")
        out[output_name] = record
    return out


def _linear(name: str, value: float, source: str, denom: float,
            output_name: str, unit: str, object_name: str) -> dict:
    source_interval = get(source)
    factor = value / denom
    if name == "m_t_pred":
        transfer = Interval.point(1)/Interval.point(2).sqrt()
    else:
        transfer = Interval.point(factor)
    propagated = transfer*Interval.bounds(source_interval["lo"], source_interval["hi"])
    low_text, high_text = propagated.decimal_bounds(40)
    lo = math.nextafter(float(low_text), -math.inf)
    hi = math.nextafter(float(high_text), math.inf)
    if not lo <= value <= hi:
        raise RuntimeError(f"{name} interval misses production")
    pset(
        output_name,
        {"lo": lo, "hi": hi, "relative_width": (hi - lo) / value,
         "source": source, "centre": value},
        provenance="DERIVED", role="internal",
        dependencies=(source, name),
        definition=QuantityDefinition(
            object=object_name, unit=unit,
            carrier="production readout linear in the certified endpoint input",
            operator=f"scale the certified {source} by the central ratio",
            source=source,
            projection=f"same readout as {name}",
            normalization="central production ratio fixed",
            scheme="linear interval propagation",
            order="same order as the production formula",
            assumptions=(f"the production formula is linear in {source}",),
            error_kind="outward interval from the certified endpoint input",
        ),
        note=f"{name} interval induced by {source}.",
    )
    annotate_interval(name, {"lo": lo, "hi": hi}, source=source,
                      note=f"linear propagation from {source}")
    return {"lo": lo, "hi": hi, "relative_width": (hi - lo) / value}


def compute() -> dict:
    v = float(get("v_HIGGS"))
    v_interval = get("v_HIGGS_interval")
    out = {}

    for name, output, unit, obj in (
        ("m_t_pred", "m_t_pred_interval", "GeV", "top mass from the endpoint VEV"),
    ):
        value = float(get(name))
        out[output] = _linear(name, value, "v_HIGGS_interval", v,
                              output, unit, obj)

    out.update(_lepton_intervals())

    bottom = bottom_endpoint_enclosure(get("kL_interval"), **{
        key: get(key) for key in ("M_P", "tau", "ns_tilt")})
    mb = float(get("m_b_pred"))
    if not bottom["lo"] <= mb <= bottom["hi"]:
        raise RuntimeError("bottom endpoint enclosure misses production")
    bottom.update(centre=mb, source="kL_interval", relative_width=(bottom["hi"]-bottom["lo"])/mb)
    pset("m_b_pred_interval", bottom, provenance="DERIVED", role="internal",
         dependencies=("kL_interval", "M_P", "tau", "ns_tilt", "m_b_pred"),
         definition=QuantityDefinition(
             object="bottom geometric mass endpoint enclosure", unit="GeV",
             carrier="same VEV and down-sector ladder as production",
             operator="v(c)/sqrt(2)*exp(-2*alpha_down(c)+tilt*(c_CMB+2*tau))",
             source="common endpoint, generated Planck scale, torsion and tilt",
             projection="m_b_pred", normalization="GeV",
             scheme="outward rational interval propagation", order="production geometric mass",
             assumptions=("Planck anchor, torsion and tilt fixed",),
             error_kind="endpoint enclosure; physical matching errors separate"),
         note="Common endpoint propagated through both the Higgs VEV and the down-sector ladder.")
    annotate_interval("m_b_pred", {key: bottom[key] for key in ("lo", "hi")},
                      source="kL_interval", note="complete VEV and down-ladder endpoint dependence")
    out["m_b_pred_interval"] = bottom

    z_response = z_endpoint_response(get("kL_interval"), centre=float(get("kL")),
                                    M_P=get("M_P"), tau=get("tau"))
    if not math.isclose(z_response["samples"][1]["M_Z_GeV"], float(get("M_Z_pred")), rel_tol=2e-10):
        raise RuntimeError("recomputed Z centre disagrees with production")
    pset("M_Z_pred_endpoint_response", z_response, provenance="DERIVED", role="internal",
         dependencies=("kL_interval", "kL", "M_P", "tau", "M_Z_pred"),
         definition=QuantityDefinition(
             object="Z mass numerical endpoint response", unit="GeV",
             carrier="production geometric two-loop gauge flow",
             operator="regenerate boundaries and solve mu=M_Z(mu) at endpoints and centre",
             source="common endpoint and generated scale inputs", projection="M_Z_pred",
             normalization="GUT-normalized hypercharge", scheme="fixed y0=1 geometric flow",
             order="two-loop gauge running, tree Z readout",
             assumptions=("Planck anchor and torsion fixed",),
             error_kind="sampled response, not a certified interval"),
         note="Replaces the VEV-only Z interval; every sample recomputes the gauge boundary and fixed point.")
    out["M_Z_pred_endpoint_response"] = z_response

    # Both the emergence scale and the generated g_R vary with this endpoint.
    m_WR = float(get("geometric_ewsb_m_WR"))
    wr = right_weak_endpoint_enclosure(get("kL_interval"), M_P=get("M_P"), tau=get("tau"))
    if not wr["lo"] <= m_WR <= wr["hi"]:
        raise RuntimeError("right weak mass interval misses production")
    wr.update(centre=m_WR, source="kL_interval", relative_width=(wr["hi"]-wr["lo"])/m_WR)
    pset("geometric_ewsb_m_WR_interval", wr, provenance="DERIVED", role="internal",
         dependencies=("kL_interval", "M_P", "tau", "geometric_ewsb_m_WR"),
         definition=QuantityDefinition(
             object="right weak mass endpoint enclosure", unit="GeV",
             carrier="generated weak boundary and emergence scale",
             operator="4*tau*M_P*pi/[c*sqrt(c^5/2+1/3-tau^2*pi/2)]",
             source="common endpoint and generated Planck and torsion inputs",
             projection="geometric_ewsb_m_WR", normalization="GeV",
             scheme="outward rational interval propagation", order="production geometric mass",
             assumptions=("Planck anchor and torsion fixed",), error_kind="endpoint enclosure"),
         note="Common endpoint propagated through both the emergence scale and the generated weak coupling.")
    annotate_interval("geometric_ewsb_m_WR", {key: wr[key] for key in ("lo", "hi")},
                      source="kL_interval", note="complete weak-boundary and emergence-scale dependence")
    out["geometric_ewsb_m_WR_interval"] = wr

    # kL_CMB = kL (1 - tau/4), tau fixed.
    kL_cmb = float(get("kL_CMB"))
    kL_interval = get("kL_interval")
    factor = 1-Interval.point(float(get("tau")))/4
    cmb = factor*Interval.bounds(math.nextafter(float(kL_interval["lo"]), -math.inf),
                               math.nextafter(float(kL_interval["hi"]), math.inf))
    low_text, high_text = cmb.decimal_bounds(40)
    lo, hi = math.nextafter(float(low_text), -math.inf), math.nextafter(float(high_text), math.inf)
    if not lo <= kL_cmb <= hi:
        raise RuntimeError("kL_CMB interval misses production")
    pset(
        "kL_CMB_interval",
        {"lo": lo, "hi": hi, "relative_width": (hi - lo) / kL_cmb,
         "source": "kL_interval", "centre": kL_cmb},
        provenance="DERIVED", role="cg",
        dependencies=("kL_interval", "tau", "kL_CMB"),
        definition=QuantityDefinition(
            object="CMB-scale window interval", unit="1",
            carrier="local endpoint window with fixed torsion quarter",
            operator="kL_CMB = kL (1 - tau/4)",
            source="kL_interval",
            projection="same readout as kL_CMB",
            normalization="tau fixed at 1/50",
            scheme="linear interval propagation",
            order="same as the production window map",
            assumptions=("tau is fixed",),
            error_kind="outward interval from the endpoint bracket",
        ),
        note="CMB window interval induced by the certified endpoint bracket.",
    )
    annotate_interval("kL_CMB", {"lo": lo, "hi": hi}, source="kL_interval",
                      note="linear propagation from the endpoint bracket")
    out["kL_CMB_interval"] = {
        "lo": lo, "hi": hi, "relative_width": (hi - lo) / kL_cmb}
    out["v_HIGGS_source"] = v_interval
    return out


if __name__ == "__main__":
    print(compute())
