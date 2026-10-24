"""Chiral charged-lepton two-point functions of the common local action.

The six diagrams are evaluated separately in tadpole-free Landau MSbar:
photon, W, Z, Higgs, neutral Goldstone and charged Goldstone. Neutrinos
are massless. These are finite renormalized coefficient functions, not
on-shell residues or independently derived generated-to-EFT thresholds.
All masses and couplings are supplied from the same leading action.

For inverse propagator pslash*(1-Sigma_L P_L-Sigma_R P_R)-(m+Omega),
the two-point variations are delta B=Omega and delta K_L/R=-Sigma_L/R.
Their first-order mass combination is Omega/m+(Sigma_L+Sigma_R)/2.
At p^2=m^2 it reproduces Martin, PRD 93, 094017 (2016), Eq. (2.20),
doi:10.1103/PhysRevD.93.094017. It is computed from the diagram numerators,
without splitting the pre-existing total mass formula by convention.

With x the boson Feynman parameter, Delta=x*V+(1-x)*f-x*(1-x)*s-i0,
B=-int log(Delta/Q^2), Bq=-int x*log(Delta/Q^2), Bk=B-Bq, and
T=int [Delta/2*(1-log(Delta/Q^2))-s*(1-x)^2*log(Delta/Q^2)].
The transverse vector numerator gives J=-B+3*Bk+1-2*(T(V)-T(0))/V,
Sigma_L/R=g_L/R^2*J/(16*pi^2), Omega=g_L*g_R*mf*(3*B-2)/(16*pi^2).
The rational terms +1 and -2 retain dimensional numerator contributions
to the MSbar finite part. For a massless vector J=0, including off shell;
integration by parts in x gives this limit without a small fictitious mass.
For a scalar, Sigma_L/R=-y_L/R^2*Bq/(16*pi^2); Omega=-y_L*y_R*mf*B/
(16*pi^2), with reversed mass sign for the neutral pseudoscalar.

Quadrature precision is selectable and locally scoped. Precision refinement
checks numerical stability; it does not bound missing perturbative orders.
"""

from __future__ import annotations

import math
from collections.abc import Mapping


SPECIES = ("electron", "muon", "tau")


def generated_lepton_action_factors():
    """Read the lepton vertices from the existing complete matter matrices.

    The colour kernel and its negative electromagnetic-charge eigenspace
    locate the two charged-lepton coordinates. The weak action distinguishes
    their chiralities. No species index, weak charge or colour covariance
    is supplied. Vanishing colour vertices exclude a direct one-loop colour
    self-energy, irrespective of the colour propagator; mixed higher loops
    are outside this statement.
    """
    import numpy as np
    from cg_core.finite_connector import matter_generators

    generators = matter_generators()
    colour = np.array([g for name, g in generators.items() if name.startswith("colour_")])
    weak = np.array([1j*generators[f"weak_{i}"] for i in (1, 2, 3)])
    y = 1j*generators["hypercharge"]
    charge = weak[2] + y
    colour_norms = np.sum(abs(colour)**2, axis=(0, 1))
    singlets = np.flatnonzero(colour_norms == 0)
    charge_values = np.diag(charge).real
    indices = singlets[charge_values[singlets] == min(charge_values[singlets])]
    weak_norms = np.sum(abs(weak)**2, axis=(0, 1))
    left = [int(i) for i in indices if weak_norms[i] > 0]
    right = [int(i) for i in indices if weak_norms[i] == 0]
    if len(left) != 1 or len(right) != 1:
        raise ArithmeticError("one left and one right charged-lepton source coordinate required")
    il, ir = left[0], right[0]
    if charge_values[il] != charge_values[ir]:
        raise ArithmeticError("the charged-lepton mass vertex must preserve electromagnetic charge")
    raising = weak[0] + 1j*weak[1]
    return {
        "electric_charge": float(charge_values[il]),
        "left_isospin": float(weak[2, il, il].real),
        "right_isospin": float(weak[2, ir, ir].real),
        "charged_current_transition_norm_squared": float(np.vdot(raising[:, il], raising[:, il]).real),
        "colour_vertex_norm_squared": float(np.sum(abs(colour[:, :, indices])**2)),
        "left_source_coordinate": il, "right_source_coordinate": ir,
        "direct_one_loop_colour_self_energy_zero": not np.any(colour[:, :, indices]),
        "source": "cg_core.finite_connector.matter_generators; complete 16-coordinate action",
    }


def charged_lepton_chiral_self_energy_one_loop(
    masses_GeV, gauge_couplings, vev_GeV, *, higgs_mass_GeV, scale_GeV,
    action_source, momentum_squared_GeV2=None, decimal_precision=45,
):
    """Return all three chiral coefficients at timelike or spacelike momenta.

    Default momenta are s=m_l^2. A mapping supplies other real momenta,
    restricted to nonzero s<=m_l^2 so no physical weak threshold is crossed.
    The exceptional zero-momentum massless-Goldstone integral is excluded.
    The -i0 branch is retained diagram by diagram. Unphysical absorptive
    parts may occur in individual Landau diagrams, even at a stable pole.
    At spacelike momenta all coefficients are real and can be compared
    as Hermitian kinetic forms in a common matching prescription.

    This function has no observation access and does not choose an
    identification between a geometric vertex and an MSbar parameter.
    """
    from mpmath.ctx_mp import MPContext

    def positive(value, name):
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"positive finite {name} required")
        return value

    if not isinstance(masses_GeV, Mapping) or set(masses_GeV) != set(SPECIES):
        raise ValueError("electron, muon and tau masses required")
    masses = {name: positive(masses_GeV[name], "mass") for name in SPECIES}
    if len(gauge_couplings) != 2:
        raise ValueError("GUT-normalized g1 and weak g2 required")
    gauge = [positive(x, "gauge coupling") for x in gauge_couplings]
    vev, higgs, scale = (positive(x, name) for x, name in
                        ((vev_GeV, "VEV"), (higgs_mass_GeV, "Higgs mass"),
                         (scale_GeV, "scale")))
    if not isinstance(action_source, str) or not action_source.strip():
        raise ValueError("nonempty action_source required")
    if type(decimal_precision) is not int or decimal_precision < 30:
        raise ValueError("decimal_precision must be an integer at least 30")
    if momentum_squared_GeV2 is None:
        momenta = {name: mass**2 for name, mass in masses.items()}
        on_shell = True
    else:
        if (not isinstance(momentum_squared_GeV2, Mapping)
                or set(momentum_squared_GeV2) != set(SPECIES)):
            raise ValueError("one real momentum squared per species required")
        momenta = {name: float(momentum_squared_GeV2[name]) for name in SPECIES}
        if any(not math.isfinite(s) or s == 0 or s > masses[name]**2
               for name, s in momenta.items()):
            raise ValueError("finite nonzero momenta at or below each tree pole required")
        on_shell = False

    mp = MPContext()
    mp.dps = decimal_precision
    g1, g = map(mp.mpf, gauge)
    v, q, h = mp.mpf(vev), mp.mpf(scale), mp.mpf(higgs)**2
    gp2, g2 = 3*g1*g1/5, g*g
    gz2 = gp2 + g2
    sw, e2 = gp2/gz2, gp2*g2/gz2
    W, Z, loop = g2*v*v/4, gz2*v*v/4, 16*mp.pi**2
    if any(mp.mpf(m)**2 >= min(W, Z/4, h/4) for m in masses.values()):
        raise ValueError("lepton masses must lie below W and half the neutral heavy masses")
    cache = {}
    factors = generated_lepton_action_factors()
    charge = mp.mpf(factors["electric_charge"])
    isospin_left, isospin_right = (mp.mpf(factors[key]) for key in ("left_isospin", "right_isospin"))
    transition = mp.sqrt(factors["charged_current_transition_norm_squared"])

    def integrals(boson, fermion, s):
        key = (boson, fermion, s)
        if key not in cache:
            def denominator(x):
                return x*boson+(1-x)*fermion-x*(1-x)*s

            def logarithm(x):
                d = denominator(x)
                return mp.log(abs(d)/(q*q)) - (mp.j*mp.pi if d < 0 else 0)

            quad = lambda f: mp.quad(f, [0, mp.mpf(".5"), mp.mpf(".99"), 1])
            b = -quad(logarithm)
            bq = -quad(lambda x: x*logarithm(x))
            t = quad(lambda x: denominator(x)/2*(1-logarithm(x))
                     - s*(1-x)**2*logarithm(x))
            cache[key] = b, bq, t
        return cache[key]

    def vector(boson, fermion, s, gl, gr, internal_mass):
        b, bq, t = integrals(boson, fermion, s)
        if boson == 0:
            j = mp.mpf(0)
        else:
            # T(0,0;0)=0, while the unused scaleless B is infrared singular.
            t0 = 0 if fermion == 0 and s == 0 else integrals(0, fermion, s)[2]
            j = -b+3*(b-bq)+1-2*(t-t0)/boson
        return gl*gl*j/loop, gr*gr*j/loop, gl*gr*internal_mass*(3*b-2)/loop

    def scalar(boson, fermion, s, yl, yr, internal_mass, mass_sign=1):
        b, bq, _ = integrals(boson, fermion, s)
        return (-yl*yl*bq/loop, -yr*yr*bq/loop,
                -mass_sign*yl*yr*internal_mass*b/loop)

    def parts(z):
        return {"real": float(mp.re(z)), "imag": float(mp.im(z))}

    def record(values, mass):
        left, right, omega = values
        return {"sigma_left": parts(left), "sigma_right": parts(right),
                "omega_GeV": parts(omega),
                "delta_mass_vertex_GeV": parts(omega),
                "delta_left_kinetic": parts(-left),
                "delta_right_kinetic": parts(-right),
                "mass_combination": parts(omega/mass+(left+right)/2)}

    output, combinations = {}, {}
    for name, mass in masses.items():
        m = mp.mpf(mass)
        s = m*m if on_shell else mp.mpf(momenta[name])
        diagrams = {
            "photon": vector(0, m*m, s, charge*mp.sqrt(e2), charge*mp.sqrt(e2), m),
            "W": vector(W, 0, s, g*transition/mp.sqrt(2), 0, 0),
            "Z": vector(Z, m*m, s, mp.sqrt(gz2)*(isospin_left-charge*sw),
                        mp.sqrt(gz2)*(isospin_right-charge*sw), m),
            "Higgs": scalar(h, m*m, s, m/v, m/v, m),
            "neutral_Goldstone": scalar(0, m*m, s, m/v, m/v, m, -1),
            "charged_Goldstone": scalar(0, 0, s, 0, mp.sqrt(2)*m/v, 0),
        }
        total = tuple(sum((d[i] for d in diagrams.values()), mp.mpf(0)) for i in range(3))
        combinations[name] = total[2]/m+(total[0]+total[1])/2
        output[name] = {"momentum_squared_GeV2": float(s), "total": record(total, m),
                        "diagrams": {key: record(value, m) for key, value in diagrams.items()}}
    weighted = sum((w*combinations[name] for w, name in zip((-1, 2, -1), SPECIES)), mp.mpf(0))
    return {
        "scheme": "MSbar", "gauge": "Landau", "vev_definition": "tadpole_free_landau",
        "action_source": action_source.strip(), "scale_GeV": scale,
        "gauge_couplings_GUT_g1_g2": gauge, "vev_GeV": vev, "higgs_mass_GeV": higgs,
        "masses_GeV": masses, "on_shell": on_shell, "species": output,
        "generated_action_factors": factors,
        "weighted_mass_combination": parts(weighted),
        "numerics": {"decimal_precision": decimal_precision, "distinct_integrals": len(cache),
                     "method": "Feynman-parameter quadrature; -i0 branch; numerical refinement required"},
        "coefficient_scope": "renormalized two-point functions, not LSZ residues or generated hard thresholds",
        "reference": "doi:10.1103/PhysRevD.93.094017; Eqs. (1.12)-(1.20), (2.20)",
    }
