# -*- coding: utf-8 -*-
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

"""Leading-universal electroweak and leading-top Z-lineshape readouts.

The production calculation uses the common-scale improved-Born
amplitudes of Denner, eqs. (8.21)--(8.25). Its retained rho contribution is
    Delta rho_bar = 3 x [1+x (19-2 pi^2)],
    x = G_F m_t^2/(8 sqrt(2) pi^2).
All neutral-current amplitudes use the same effective weak angle and
rho_NC=1/(1-Delta rho_bar). The non-universal bottom amplitude has
delta g_V=delta g_A=x before multiplication by sqrt(rho_NC). Its width
retains the interference 2 x(g_V+g_A). The partial widths, inclusive
widths, ratios and peak cross section are computed from these amplitudes
with the factorized massless QCD/QED radiators. The generated alpha_Z
is the common effective electromagnetic input at the Z reference scale.

The two-point and self-energy expressions form a separate diagnostic
implementation; their complete on-shell solver requires analytic
zero-momentum and massless limits before use as an observable solver.
Their light-quark effective masses follow Denner, eq. (8.10). The
comparison calculation evaluates the production approximation on an
independently specified reference set.
Published predictions use the framework inputs; measured values are
comparison targets.

References
----------
A. Denner, "Techniques for calculation of electroweak radiative corrections
at the one-loop level and results for W-physics at LEP200",
Fortschr. Phys. 41 (1993) 307; arXiv:0709.1075.
A. Sirlin, Phys. Rev. D 22 (1980) 971.
A. Akhundov, D. Bardin and T. Riemann, Nucl. Phys. B 276 (1986) 1.
W. Beenakker and W. Hollik, Z. Phys. C 40 (1988) 141.
J. Erler and A. Freitas, "Electroweak Model and Constraints on New Physics",
in S. Navas et al. (Particle Data Group), Phys. Rev. D 110 (2024) 030001,
eqs. (10.53)--(10.55), (10.76)--(10.77).

Equation numbers in the function documentation refer to Denner.
"""

from __future__ import annotations

import cmath
import math
import sys
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset, sm_value, compare_and_set  # noqa: E402
from cg_core.electroweak import (  # noqa: E402
    bottom_vertex_width_shift, heavy_top_x, leading_rho_bar,
    leading_universal_parameters, neutral_current_widths, veltman_delta_rho,
)


# =========================================================================
#  1.  The scalar two-point function B0  (Denner eq. 4.23), MS-bar
# =========================================================================


def _B0(p2: complex, m0: float, m1: float, mu: float) -> complex:
    """Scalar two-point function B0(p^2; m0, m1), MS-bar subtracted.

    Denner eq. (4.23):

        B0 = Delta + 2 - ln(m0 m1/mu^2)
             + (m0^2-m1^2)/p^2 ln(m1/m0) - (m0 m1/p^2)(1/r - r) ln r

    with r + 1/r = (m0^2+m1^2-p^2 - i eps)/(m0 m1), |r|<=1, r never crossing
    the negative real axis.  The universal UV divergence
    Delta = 2/(4-D) - gamma_E + ln(4 pi) is dropped (MS-bar); the finite
    constant +2 is retained.  Special limits (one/two massless lines) are
    implemented analytically.

    Returns a complex number (the imaginary part encodes the threshold/i eps
    branch).  All masses in GeV; mu is the MS renormalisation scale in GeV.
    """
    p2 = complex(p2)
    m0 = abs(float(m0))
    m1 = abs(float(m1))
    m0sq = m0 * m0
    m1sq = m1 * m1

    # ---- p^2 = 0 ----
    if abs(p2) < 1e-14:
        if m0 == 0.0 and m1 == 0.0:
            raise ValueError("B0(0; 0, 0) is IR divergent (only finite "
                             "differences are used)")
        if m0 == m1 and m0 > 0:
            # B0(0; m, m) = Delta - ln(m^2/mu^2)   [the +2 cancels the
            # (1/r-r) ln r term at p^2=0]  ->  -ln(m^2/mu^2)  (MS-bar)
            return -cmath.log(m0sq / mu**2)
        if m0 == 0.0 or m1 == 0.0:
            # one massless line: B0(0;0,m) = 1 - ln(m^2/mu^2)
            mz = m1 if m0 == 0.0 else m0
            return 1.0 - cmath.log(mz * mz / mu**2)
        # general m0 != m1, both massive
        #   B0(0;m0,m1) = Delta + 1
        #        - [ m0^2 ln(m0^2/mu^2) - m1^2 ln(m1^2/mu^2) ]/(m0^2 - m1^2)
        num = m0sq * cmath.log(m0sq / mu**2) - m1sq * cmath.log(m1sq / mu**2)
        return 1.0 - num / (m0sq - m1sq)

    # ---- p^2 != 0 ----
    if m0 == 0.0 and m1 == 0.0:
        # two massless lines (appears only in IR-singular difference terms;
        # B0(p^2;0,0) = Delta + 2 - ln(-p^2/mu^2) - i pi for p^2>0)
        return 2.0 - cmath.log((-p2) / mu**2)
    if m0 == 0.0 or m1 == 0.0:
        # one massless, one mass m
        m = m1 if m0 == 0.0 else m0
        msq = m * m
        # B0(p^2;0,m) = 2 - ln(m^2/mu^2) - (1 - m^2/p^2) ln(1 - p^2/m^2 - i eps)
        z = 1.0 - p2 / msq
        if abs(z.imag) < 1e-300 and z.real <= 0.0:
            z = complex(z.real, -1e-20)  # -i eps just below the cut
        return 2.0 - cmath.log(msq / mu**2) - (1.0 - msq / p2) * cmath.log(z)

    # ---- general m0>0, m1>0 ----
    K = (m0sq + m1sq - p2) / (m0 * m1)          # r + 1/r = K  (eq. 4.24)
    if abs(p2.imag) < 1e-300 and p2.real > (m0 + m1) ** 2:
        K = K - 1e-12j                            # -i eps above threshold
    disc = K * K - 4.0
    r = (K - cmath.sqrt(disc)) / 2.0
    if abs(r) > 1.0:                              # enforce |r| <= 1
        r = 1.0 / r
    val = (2.0 - cmath.log(m0 * m1 / mu**2)
           + (m0sq - m1sq) / p2 * cmath.log(m1 / m0)
           - (m0 * m1 / p2) * (1.0 / r - r) * cmath.log(r))
    return val


def _dB0dp2_at0(m0: float, m1: float) -> complex:
    """Partial momentum derivative of B0 at p^2 = 0 (Denner eq. 4.25 limit).

    Used solely for Pi_AA(0) = d Sigma_AA/dk^2|_0  (Denner eq. 8.5).  For the
    equal-mass case we use the well-known limit dB0/dp^2|_0 = 1/(6 m^2).
    """
    m0 = abs(float(m0))
    m1 = abs(float(m1))
    if m0 == m1:
        return 1.0 / (6.0 * m0 * m0)
    # general / one-massless cases are not needed for Pi_AA(0) (only the
    # equal-mass fermion and the W-W insertion are used); kept as a guard.
    raise NotImplementedError("dB0/dp^2|_0 only implemented for equal masses")


# =========================================================================
#  2.  Fermion spectrum + couplings  (Denner eq. A.14, A.15)
# =========================================================================
def _fermion_set(mt: float, mb: float, *, light_up=(0.041, 1.5),
                 light_down=(0.041, 0.15), lep=("m_e", "m_mu", "m_tau"),
                 m_e=0.000511, m_mu=0.1056583745, m_tau=1.77686) -> list:
    """The SM fermion content with (name, Q, I3, N_c, mass).

    Q is the electric charge, I3 the weak isospin, N_c the colour factor.
    The light-quark masses for u/c (light_up) and d/s (light_down) are
    Denner's *effective* masses (eq. 8.10) that reproduce the hadronic
    vacuum polarisation; b and t are the physical masses.  Leptons are the
    three charged leptons plus three massless neutrinos.
    """
    f = []
    for name, q, i3, m in (("e", -1, -0.5, m_e),
                           ("mu", -1, -0.5, m_mu),
                           ("tau", -1, -0.5, m_tau)):
        f.append((name, q, i3, 1.0, m))
    for name, q, i3, m in (("nu_e", 0, 0.5, 0.0),
                           ("nu_mu", 0, 0.5, 0.0),
                           ("nu_tau", 0, 0.5, 0.0)):
        f.append((name, q, i3, 1.0, m))
    # up-type quarks (Q=2/3, I3=1/2)
    f.append(("u", 2.0 / 3.0, 0.5, 3.0, light_up[0]))
    f.append(("c", 2.0 / 3.0, 0.5, 3.0, light_up[1]))
    f.append(("t", 2.0 / 3.0, 0.5, 3.0, mt))
    # down-type quarks (Q=-1/3, I3=-1/2)
    f.append(("d", -1.0 / 3.0, -0.5, 3.0, light_down[0]))
    f.append(("s", -1.0 / 3.0, -0.5, 3.0, light_down[1]))
    f.append(("b", -1.0 / 3.0, -0.5, 3.0, mb))
    return f


def _couplings(q: float, i3: float, s2: float):
    """Denner eq. A.14:  g^+_f = -(s/c) Q_f ; g^-_f = (I3 - s^2 Q_f)/(s c)."""
    s = math.sqrt(s2)
    c = math.sqrt(1.0 - s2)
    gp = -(s / c) * q
    gm = (i3 - s2 * q) / (s * c)
    return gp, gm


# =========================================================================
#  3.  The four transverse gauge-boson self-energies  (Denner eq. B.1-B.4)
# =========================================================================
def _sigma_AA(k2: complex, ferm, MW, s2, alpha, mu) -> complex:
    """Eq. (B.1)."""
    res = 0.0 + 0.0j
    for _name, q, _i3, nc, mf in ferm:
        if q == 0.0:
            continue
        b0 = _B0(k2, mf, mf, mu)
        b0_0 = _B0(0.0, mf, mf, mu)
        res += nc * q * q * (-(k2 + 2 * mf * mf) * b0
                             + 2 * mf * mf * b0_0 + k2 / 3.0)
    b0w = _B0(k2, MW, MW, mu)
    b0w0 = _B0(0.0, MW, MW, mu)
    res += (3.0 * k2 + 4.0 * MW * MW) * b0w - 4.0 * MW * MW * b0w0
    return -(alpha / (4.0 * math.pi)) * (2.0 / 3.0) * res


def _sigma_AZ(k2: complex, ferm, MW, s2, c2, alpha, mu) -> complex:
    """Eq. (B.2).  The boson brace is multiplied by -1/(3 s c)."""
    sc = math.sqrt(s2 * c2)
    res = 0.0 + 0.0j
    for _name, q, i3, nc, mf in ferm:
        if q == 0.0:
            continue
        gp, gm = _couplings(q, i3, s2)
        b0 = _B0(k2, mf, mf, mu)
        b0_0 = _B0(0.0, mf, mf, mu)
        res += nc * (-q) * (gp + gm) * (-(k2 + 2 * mf * mf) * b0
                                        + 2 * mf * mf * b0_0 + k2 / 3.0)
    b0w = _B0(k2, MW, MW, mu)
    b0w0 = _B0(0.0, MW, MW, mu)
    brace = ((9.0 * c2 + 0.5) * k2 + (12.0 * c2 + 4.0) * MW * MW) * b0w \
        - (12.0 * c2 - 2.0) * MW * MW * b0w0 + k2 / 3.0
    res -= brace / (3.0 * sc)
    return -(alpha / (4.0 * math.pi)) * (2.0 / 3.0) * res


def _sigma_ZZ(k2: complex, ferm, MW, MZ, MH, s2, c2, alpha, mu) -> complex:
    """Eq. (B.3)."""
    s2c2 = s2 * c2
    res = 0.0 + 0.0j
    for _name, q, i3, nc, mf in ferm:
        gp, gm = _couplings(q, i3, s2)
        b0 = _B0(k2, mf, mf, mu)
        b0_0 = _B0(0.0, mf, mf, mu)
        res += nc * ((gp ** 2 + gm ** 2) * (-(k2 + 2 * mf * mf) * b0
                    + 2 * mf * mf * b0_0 + k2 / 3.0)
                     + 3.0 / (4.0 * s2c2) * mf * mf * b0)
    # W-W loop
    b0w = _B0(k2, MW, MW, mu)
    b0w0 = _B0(0.0, MW, MW, mu)
    brace_w = ((18 * c2 ** 2 + 2 * c2 - 0.5) * k2
               + (24 * c2 ** 2 + 16 * c2 - 10) * MW * MW) * b0w \
        - (24 * c2 ** 2 - 8 * c2 + 2) * MW * MW * b0w0 \
        + (4 * c2 - 1) * k2 / 3.0
    res += brace_w / (6.0 * s2c2)
    # Z-H loop
    b0zh = _B0(k2, MZ, MH, mu)
    b0zh0 = _B0(0.0, MZ, MH, mu)
    b0z0 = _B0(0.0, MZ, MZ, mu)
    b0h0 = _B0(0.0, MH, MH, mu)
    brace_h = (2 * MH ** 2 - 10 * MZ ** 2 - k2) * b0zh \
        - 2 * MZ ** 2 * b0z0 - 2 * MH ** 2 * b0h0 \
        - (MZ ** 2 - MH ** 2) ** 2 / k2 * (b0zh - b0zh0) - (2.0 / 3.0) * k2
    res += brace_h / (12.0 * s2c2)
    return -(alpha / (4.0 * math.pi)) * (2.0 / 3.0) * res


def _sigma_W(k2: complex, ferm, MW, MZ, MH, s2, c2, alpha, mu, lam=1e-6) -> complex:
    """Eq. (B.4).  lam is the (small) photon-mass IR regulator of the W-gamma
    loop; only the finite combinations enter Delta r (eq. 8.14), so the
    result is insensitive to lam once it is small."""
    s2v = s2
    res = 0.0 + 0.0j
    # charged leptons (each with a massless neutrino partner)
    for _name, q, i3, _nc, ml in [f for f in ferm if f[0] in ("e", "mu", "tau")]:
        b0 = _B0(k2, 0.0, ml, mu)
        b00 = _B0(0.0, ml, ml, mu)
        b0_00 = _B0(0.0, 0.0, ml, mu)
        res += -(k2 - ml * ml / 2.0) * b0 + k2 / 3.0 \
            + ml * ml * b00 + ml ** 4 / (2.0 * k2) * (b0 - b0_00)
    # quark doublets (diagonal CKM, |V_ii|^2 = 1, colour factor 3)
    up = {"u": 0.0, "c": 0.0, "t": 0.0}
    dn = {"d": 0.0, "s": 0.0, "b": 0.0}
    for _n, _q, _i3, _nc, m in ferm:
        if _n in up:
            up[_n] = m
        if _n in dn:
            dn[_n] = m
    for u, d in (("u", "d"), ("c", "s"), ("t", "b")):
        muq, mdq = up[u], dn[d]
        b0 = _B0(k2, muq, mdq, mu)
        b00 = _B0(0.0, muq, mdq, mu)
        b0uu0 = _B0(0.0, muq, muq, mu)
        b0dd0 = _B0(0.0, mdq, mdq, mu)
        res += -(k2 - (muq ** 2 + mdq ** 2) / 2.0) * b0 + k2 / 3.0 \
            + muq ** 2 * b0uu0 + mdq ** 2 * b0dd0 \
            + (muq ** 2 - mdq ** 2) ** 2 / (2.0 * k2) * (b0 - b00)
    res *= 3.0  # N_c
    termA = (2.0 / 3.0) * (1.0 / (2.0 * s2v)) * res
    # W-gamma (lambda) loop
    b0wg = _B0(k2, MW, lam, mu)
    b0wg0 = _B0(0.0, MW, lam, mu)
    b0w0 = _B0(0.0, MW, MW, mu)
    termB = (2.0 / 3.0) * ((2 * MW ** 2 + 5 * k2) * b0wg
                           - 2 * MW ** 2 * b0w0
                           - MW ** 4 / k2 * (b0wg - b0wg0) + k2 / 3.0)
    # W-Z loop
    b0wz = _B0(k2, MW, MZ, mu)
    b0wz0 = _B0(0.0, MW, MZ, mu)
    b0z0 = _B0(0.0, MZ, MZ, mu)
    termC = (1.0 / (12.0 * s2v)) * (
        ((40 * c2 - 1) * k2 + (16 * c2 + 54 - 10 / c2 ** 2) * MW * MW) * b0wz
        - (16 * c2 + 2) * (MW ** 2 * b0w0 + MZ ** 2 * b0z0)
        + (4 * c2 - 1) * (2.0 / 3.0) * k2
        - (8 * c2 + 1) * (MW ** 2 - MZ ** 2) ** 2 / k2 * (b0wz - b0wz0))
    # W-H loop
    b0wh = _B0(k2, MW, MH, mu)
    b0wh0 = _B0(0.0, MW, MH, mu)
    b0h0 = _B0(0.0, MH, MH, mu)
    termD = (1.0 / (12.0 * s2v)) * (
        (2 * MH ** 2 - 10 * MW ** 2 - k2) * b0wh
        - 2 * MW ** 2 * b0w0 - 2 * MH ** 2 * b0h0
        - (MW ** 2 - MH ** 2) ** 2 / k2 * (b0wh - b0wh0)
        - (2.0 / 3.0) * k2)
    return -(alpha / (4.0 * math.pi)) * (termA + termB + termC + termD)


def _PiAA0(ferm, MW, s2, alpha, mu) -> complex:
    """Pi_AA(0) = d Sigma_AA/dk^2|_0  (Denner eq. 8.5).

    Analytic derivative using dB0/dp^2|_0 = 1/(6 m^2) for the equal-mass
    fermion/W insertions.
    """
    res = 0.0 + 0.0j
    for _name, q, _i3, nc, mf in ferm:
        if q == 0.0:
            continue
        b0_0 = _B0(0.0, mf, mf, mu)
        b0p = _dB0dp2_at0(mf, mf)
        res += nc * q * q * (-b0_0 - 2 * mf * mf * b0p + 1.0 / 3.0)
    b0w0 = _B0(0.0, MW, MW, mu)
    b0wp = _dB0dp2_at0(MW, MW)
    res += 3.0 * b0w0 + 4.0 * MW * MW * b0wp
    return -(alpha / (4.0 * math.pi)) * (2.0 / 3.0) * res


# =========================================================================
#  4.  Two-point representation of Delta r and its diagnostic iteration
# =========================================================================
def delta_r(ferm, MW, MZ, MH, s2, alpha, mu, lam=1e-6) -> complex:
    """Full one-loop Delta r (Denner eq. 8.14).

        Delta r = Pi_AA(0)
                - (c^2/s^2)[ Sigma_ZZ(M_Z^2)/M_Z^2 - Sigma_W(M_W^2)/M_W^2 ]
                + [ Sigma_W(0) - Sigma_W(M_W^2) ]/M_W^2
                + 2(c/s) Sigma_AZ(0)/M_Z^2
                + alpha/(4 pi s^2)[ 6 + (7-4 s^2)/(2 s^2) ln c^2 ]

    Returns the (complex) Delta r; the imaginary part is discarded in the
    M_W solve.  mu and lam drop out of the real part (physical result).
    """
    c2 = 1.0 - s2
    Pi = _PiAA0(ferm, MW, s2, alpha, mu)
    Szz = _sigma_ZZ(MZ * MZ, ferm, MW, MZ, MH, s2, c2, alpha, mu)
    Sw = _sigma_W(MW * MW, ferm, MW, MZ, MH, s2, c2, alpha, mu, lam)
    Sw0 = _sigma_W(0.0, ferm, MW, MZ, MH, s2, c2, alpha, mu, lam)
    Saz0 = _sigma_AZ(0.0, ferm, MW, s2, c2, alpha, mu)
    dr = (Pi - c2 / s2 * (Szz / MZ ** 2 - Sw / MW ** 2)
          + (Sw0 - Sw) / MW ** 2
          + 2.0 * math.sqrt(c2 / s2) * Saz0 / MZ ** 2
          + alpha / (4.0 * math.pi * s2)
          * (6.0 + (7.0 - 4.0 * s2) / (2.0 * s2) * math.log(c2)))
    return dr


def solve_MW(alpha, G_F, MZ, MH, mt, mb, *, mu=None, verbose=False,
             light_up=(0.041, 1.5), light_down=(0.041, 0.15), lam=1e-6,
             max_iter=40) -> dict:
    """Diagnostic iteration of the on-shell Sirlin relation, Denner Eq. (8.13).

        M_W^2 (1 - M_W^2/M_Z^2) = (pi alpha)/(sqrt(2) G_F) [1 + Delta r]

    The two-point representation requires analytic zero-momentum and
    massless finite limits before it supplies a complete observable
    calculation. Production uses the separately defined common effective
    neutral-current amplitude. This diagnostic iterates M_W through
    s^2=1-M_W^2/M_Z^2 and the two-point arguments.
    """
    MZ = float(MZ)
    if not all(math.isfinite(x) and x > 0 for x in (alpha, G_F, MZ, MH)):
        raise ValueError("W solver inputs alpha, G_F, MZ and MH must be positive")
    if mu is None:
        mu = MZ
    M_W = math.sqrt(MZ * MZ * 0.777)   # initial guess ~ 80.4
    dr_val = 0.0 + 0.0j
    s2 = 0.0
    A = math.pi * alpha / (math.sqrt(2.0) * G_F * MZ * MZ)
    last = None
    for iteration in range(1, max_iter + 1):
        s2 = 1.0 - (M_W / MZ) ** 2
        ferm = _fermion_set(mt, mb, light_up=light_up,
                            light_down=light_down)
        dr_val = delta_r(ferm, M_W, MZ, MH, s2, alpha, mu, lam)
        dr_re = dr_val.real
        #  M_W^2 (1 - M_W^2/M_Z^2) = A [1 + Dr]   ->  s^2 c^2 = A[1+Dr]
        s2c2 = A * (1.0 + dr_re)
        # s^2 (1 - s^2) = s2c2  ->  s^2 = (1 - sqrt(1-4 s2c2))/2
        disc = 1.0 - 4.0 * s2c2
        if not math.isfinite(s2c2) or not 0 < s2c2 <= 0.25:
            raise ValueError("M_W solve: 1-4 s2c2 < 0 (Delta r too large)")
        s2_new = 0.5 * (1.0 - math.sqrt(disc))
        M_W_new = MZ * math.sqrt(1.0 - s2_new)
        if last is not None and abs(M_W_new - last) / M_W_new < 1e-10:
            M_W = M_W_new
            break
        last = M_W_new
        M_W = M_W_new
    else:
        raise RuntimeError("one-loop M_W iteration did not converge")
    s2 = 1.0 - (M_W / MZ) ** 2
    c2 = 1.0 - s2
    dr_val = delta_r(ferm, M_W, MZ, MH, s2, alpha, mu, lam)
    rhs = A * (1.0 + dr_val.real)
    relative_residual = (s2 * c2 - rhs) / max(abs(rhs), 1e-15)
    if not math.isfinite(relative_residual) or abs(relative_residual) > 2e-9:
        raise RuntimeError("one-loop M_W failed its original equation residual")
    return {"M_W": M_W, "s2": s2, "c2": c2, "Delta_r": dr_val.real,
            "Delta_r_imag": dr_val.imag, "converged": True,
            "iterations": iteration, "relative_residual": relative_residual}


# =========================================================================
#  5.  Improved-Born effective couplings  (Denner eq. 8.20 - 8.25)
# =========================================================================
def delta_alpha(ferm, MZ, alpha, mu) -> complex:
    """The full fermionic running of alpha, Delta alpha(M_Z^2)
    (Denner eq. 8.16 / 8.19).  Returned as a complex (real part physical).

        Delta alpha(s) = Pi_AA(0) - Re Pi_AA(s) = sum_f (alpha/3 pi) N_c Q_f^2
                         [ ln(s/m_f^2) - 5/3 ]  (leading-log + finite)
    """
    res = 0.0 + 0.0j
    for _name, q, _i3, nc, mf in ferm:
        if q == 0.0 or mf == 0.0:
            continue
        # B0(M_Z^2,m_f,m_f) - B0(0,m_f,m_f)  times the (2/3) sigma-structure
        b0 = _B0(MZ * MZ, mf, mf, mu)
        b0_0 = _B0(0.0, mf, mf, mu)
        # Sigma_AA(MZ^2)/MZ^2 - Sigma_AA(0)/0  limit:
        res += nc * q * q * (b0_0 - b0)
    # Pi_AA(0) - Pi_AA(M_Z^2)  with Pi = Sigma/k^2 :
    return (alpha / (3.0 * math.pi)) * res


def delta_rho(G_F, mt, mb=0.0) -> float:
    """One-loop t-b doublet rho parameter (Veltman):

        Delta rho = 3 G_F/(8 pi^2 sqrt(2)) [ mt^2 + mb^2
                    - 2 mt^2 mb^2/(mt^2-mb^2) ln(mt^2/mb^2) ]

    Shared stable implementation with ew_precision.delta_rho, including
    the custodial and single-massless limits.
    """
    return veltman_delta_rho(G_F, mt, mb)


def delta_rho_bar(G_F, mt) -> float:
    """Two-loop irreducible leading m_t^2 rho parameter (Denner eq. 8.22):

        Delta rho_bar = (3 G_F m_t^2/(8 sqrt2 pi^2))
        [ 1 + (G_F m_t^2/(8 sqrt2 pi^2))(19 - 2 pi^2) ]

    The alpha -> G_F replacement gives the correct leading O(alpha^2) term
    (van der Bij - Hoogeveen; Consoli - Hollik - Jegerlehner).
    """
    return leading_rho_bar(G_F, mt)


def delta_alpha_ferm(ferm, MZ, alpha, mu):
    """Delta alpha_ferm = 1 - alpha/alpha(M_Z)  (the resummed running,
    eq. 8.19).  Uses Delta alpha(M_Z^2) = Pi_AA(0) - Pi_AA(M_Z^2)."""
    da = delta_alpha(ferm, MZ, alpha, mu).real
    return da


def sin2theta_eff(ferm, s2, MW, MZ, mt, mb, G_F, alpha, mu,
                  alpha_had=0.0) -> dict:
    """Improved-Born effective mixing, sin^2 theta_eff^l (Denner eq. 8.20-8.25).

    sbar^2 = s^2 + c^2 Delta rho_bar   (eq. 8.21)
    with Delta rho_bar (eq. 8.22) and the resummed running alpha(s) (8.19).
    Returns {s2_eff, Delta_alpha, Delta_rho_bar, Delta_alpha_had}.
    """
    c2 = 1.0 - s2
    d_rho_bar = delta_rho_bar(G_F, mt)
    d_rho = delta_rho(G_F, mt, mb)
    da_ferm = delta_alpha_ferm(ferm, MZ, alpha, mu)
    # improved-Born:  sbar^2 = s^2 + c^2 d_rho_bar
    s2_eff = s2 + c2 * d_rho_bar
    return {"s2_eff": s2_eff, "delta_rho": d_rho, "delta_rho_bar": d_rho_bar,
            "delta_alpha": da_ferm}


# =========================================================================
#  6.  Leading-top contribution to the Z -> b bbar width
# =========================================================================

def delta_gamma_b_top(G_F, mt, s2_eff) -> dict:
    """Non-universal heavy-top amplitude and relative width interference.

    delta g_V=delta g_A=x_t in the common effective neutral-current
    basis. The relative width therefore depends on that basis's weak
    angle. Its common rho_NC normalization cancels in this ratio.
    """
    x_t = heavy_top_x(G_F, mt)
    return {"delta_gamma_b_leading": bottom_vertex_width_shift(s2_eff, x_t),
            "delta_gV": x_t, "delta_gA": x_t,
            "delta_rho_1loop": 3.0 * x_t}


def mw_leading_universal(M_Z: float, alpha_Z: float, G_F: float,
                         d_rho_bar: float) -> float:
    """Mass readout of the common-scale Denner effective-parameter relation.

    This is the leading-universal closure level used by the framework:
    running alpha plus the improved-Born rho resummation, without the
    non-universal remainder.
    """
    return leading_universal_parameters(M_Z, alpha_Z, G_F, d_rho_bar)["M_W"]


def compute() -> dict:
    """Publish one common effective neutral-current amplitude and its widths."""
    v = float(get("v_HIGGS"))
    M_Z = float(get("M_Z_pred"))
    mt = float(get("m_t_pred"))
    mb = float(get("m_b_pred"))
    alpha_MZ = 1.0 / float(get("alpha_inv_MZ_pred"))
    alpha_s_MZ = float(get("alpha_s_MZ_pred"))
    G_F = 1.0 / (math.sqrt(2.0) * v * v)

    d_rho_2 = delta_rho_bar(G_F, mt)
    d_rho_1 = delta_rho(G_F, mt, mb)
    effective = leading_universal_parameters(M_Z, alpha_MZ, G_F, d_rho_2)
    M_W_lu, s2_eff = effective["M_W"], effective["s2_eff"]
    rho_nc = effective["rho_nc"]
    top = delta_gamma_b_top(G_F, mt, s2_eff)
    x_t = top["delta_gV"]
    delta_b = top["delta_gamma_b_leading"]
    widths = neutral_current_widths(M_Z, s2_eff, G_F, alpha_MZ, alpha_s_MZ,
                                   rho_nc=rho_nc, x_t=x_t)
    shared_inputs = ("M_Z_pred", "alpha_inv_MZ_pred", "v_HIGGS", "m_t_pred")
    quark_inputs = shared_inputs + ("alpha_s_MZ_pred",)
    Gamma_b_corr, Gamma_had_corr, Gamma_Z_corr = (
        widths["b"], widths["had"], widths["Z"])
    Gamma_e = widths["e"]

    pset("delta_rho_2loop", d_rho_2, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "m_t_pred"),
         note=f"Delta rho_bar = {d_rho_2:.7f} from Denner eq. 8.22, with "
              f"x = G_F m_t^2/(8 sqrt2 pi^2) and the framework m_t = "
              f"{mt:.3f} GeV; one-loop t-b rho = {d_rho_1:.7f}.")
    pset("deltab_top_vertex", delta_b, provenance="DERIVED", role="internal",
         dependencies=shared_inputs,
         note=f"Delta_b = {delta_b:.9f}: relative heavy-top width interference "
              "2 x_t (g_V+g_A)/(g_V^2+g_A^2) at the common effective weak angle; "
              "delta g_V=delta g_A=x_t before the common sqrt(rho_NC) factor.")
    pset("rho_NC_leading", rho_nc, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "m_t_pred"),
         note="Common neutral-current normalization 1/(1-Delta rho_bar), "
              "Denner eq. (8.25), multiplying the squared effective amplitude once.")
    pset("z_pole_partial_widths", widths, provenance="DERIVED", role="internal",
         dependencies=quark_inputs,
         note="Partial and summed Z widths in GeV from the common improved-Born "
              "angle and rho_NC, with one-loop bottom interference and factorized "
              "massless non-singlet QCD (through alpha_s^2) and leading QED radiators.")
    for key, value, dependencies, note in (
        ("Gamma_l_pred_lead1loop", widths["l"], shared_inputs,
         "Sum of the three charged-lepton widths from the common effective amplitude."),
        ("Gamma_inv_pred_lead1loop", widths["nu"],
         ("M_Z_pred", "v_HIGGS", "m_t_pred"),
         "Sum of the three massless-neutrino widths with the common rho_NC."),
        ("sin2_theta_eff_b_pred", s2_eff * (1.0 + 2.0 * x_t), shared_inputs,
         "Bottom effective angle sbar_b^2=sbar_l^2(1+2 x_t) through first order "
         "in the non-universal heavy-top amplitude."),
    ):
        pset(key, value, provenance="DERIVED", role="internal",
             dependencies=dependencies, note=note)
    compare_and_set("Gamma_b_pred_1loop", Gamma_b_corr,
                    sm_value("Gamma_b_obs"),
                    dependencies=quark_inputs,
                    note=f"Gamma_b = {Gamma_b_corr:.9f} GeV from the common "
                         "effective neutral-current amplitude and leading-top "
                         "interference, with factorized massless QCD/QED radiators.")

    for key, value, observed_key, symbol in (
        ("Gamma_had_pred_lead1loop", Gamma_had_corr,
         "Gamma_had_obs", "Gamma_had"),
        ("Gamma_Z_pred_lead1loop", Gamma_Z_corr,
         "Gamma_Z_obs", "Gamma_Z"),
    ):
        compare_and_set(
            key, value, sm_value(observed_key),
            dependencies=quark_inputs,
            note=f"{symbol} = {value:.9f} GeV: sum of partial widths from the "
                 "common effective neutral-current amplitude, with the leading-top "
                 "bottom interference and retained factorized QCD/QED radiators.")

    Gamma_b_corr = float(get("Gamma_b_pred_1loop"))
    Gamma_had_corr = float(get("Gamma_had_pred_lead1loop"))
    Gamma_Z_corr = float(get("Gamma_Z_pred_lead1loop"))
    Gamma_e = float(get("Gamma_l_pred_lead1loop")) / 3.0
    if min(Gamma_b_corr, Gamma_had_corr, Gamma_Z_corr, Gamma_e, M_Z) <= 0.0:
        raise ValueError("Z widths and mass must be positive")
    R_b_corr = Gamma_b_corr / Gamma_had_corr
    R_l_corr = Gamma_had_corr / Gamma_e
    sigma_had_corr = (12.0 * math.pi * Gamma_e * Gamma_had_corr
                     / (M_Z**2 * Gamma_Z_corr**2) * 3.89379e5)
    compare_and_set(
        "R_b_pred_lead1loop", R_b_corr, sm_value("R_b_obs"),
        dependencies=("Gamma_b_pred_1loop", "Gamma_had_pred_lead1loop"),
        note="Gamma_b/Gamma_had from one common set of effective partial widths.")
    compare_and_set(
        "R_l_pred_lead1loop", R_l_corr, sm_value("R_l_obs"),
        dependencies=("Gamma_had_pred_lead1loop", "Gamma_l_pred_lead1loop"),
        note="Gamma_had/Gamma_e, with Gamma_e one third of the common "
             "effective charged-lepton width in the massless approximation.")
    compare_and_set(
        "sigma_had_pred_lead1loop", sigma_had_corr, sm_value("sigma_had_obs"),
        dependencies=("M_Z_pred", "Gamma_l_pred_lead1loop", "Gamma_had_pred_lead1loop",
                      "Gamma_Z_pred_lead1loop"),
        note="12 pi Gamma_e Gamma_had/(M_Z^2 Gamma_Z^2), with "
             "1 GeV^-2=3.89379e5 nb and all partial and inclusive widths "
             "from the common effective neutral-current amplitude.")
    compare_and_set("M_W_pred_lead1loop", M_W_lu, sm_value("m_W_obs"),
                    dependencies=shared_inputs,
                    note=f"M_W = {M_W_lu:.4f} GeV from the "
                         f"leading-universal on-shell relation pi "
                         f"alpha_Z/sbar^2_W = sqrt2 G_F M_W^2 at the common "
                         f"Z reference scale, with the retained heavy-top rho "
                         f"(Denner eqs. 8.22--8.25).")
    compare_and_set("sin2_theta_eff_l_pred", s2_eff,
                    sm_value("sin2thetaW_eff_obs"),
                    dependencies=shared_inputs,
                    note=f"sin^2 theta_eff^l = {s2_eff:.6f} from "
                         f"the improved-Born relation sbar^2_W = "
                         f"s^2_W + c^2_W Delta_rho_bar (Denner eq. 8.21).")

    return {
        "G_F": G_F,
        "delta_rho_1loop": d_rho_1,
        "delta_rho_2loop": d_rho_2,
        "delta_b": delta_b,
        "rho_NC": rho_nc,
        "partial_widths": widths,
        "Gamma_l_corr": widths["l"],
        "Gamma_inv_corr": widths["nu"],
        "sin2theta_eff_b": s2_eff * (1.0 + 2.0 * x_t),
        "Gamma_b_corr": Gamma_b_corr,
        "Gamma_had_corr": Gamma_had_corr,
        "Gamma_Z_corr": Gamma_Z_corr,
        "R_b_corr": R_b_corr,
        "R_l_corr": R_l_corr,
        "sigma_had_corr_nb": sigma_had_corr,
        "M_W_leading_universal": M_W_lu,
        "sin2theta_eff_l": s2_eff,
    }


def formula_check() -> dict:
    """Evaluate the retained effective-amplitude formulas on reference inputs."""
    G_F = sm_value("G_F_obs")
    mt = sm_value("m_t_obs")
    M_Z = sm_value("M_Z")
    alpha_MZ = 1.0 / sm_value("alpha_inv_MZ_obs")
    d_rho_2 = delta_rho_bar(G_F, mt)
    effective = leading_universal_parameters(M_Z, alpha_MZ, G_F, d_rho_2)
    delta_b = delta_gamma_b_top(G_F, mt, effective["s2_eff"])["delta_gamma_b_leading"]
    M_W_lu = effective["M_W"]
    return {
        "delta_rho_2loop": d_rho_2,
        "delta_b": delta_b,
        "delta_b_pct": delta_b * 100.0,
        "M_W_leading_universal": M_W_lu,
        "M_W_exp": sm_value("m_W_obs"),
    }


def main() -> int:
    r = compute()
    fc = formula_check()
    print("=" * 72)
    print("  V5 LEADING-UNIVERSAL AND LEADING-TOP EW READOUTS")
    print("=" * 72)
    print(f"  M_W lead-univ     = {r['M_W_leading_universal']:.4f} GeV")
    print(f"  Gamma_b lead-top  = {r['Gamma_b_corr']:.5f} GeV")
    print(f"  Gamma_had         = {r['Gamma_had_corr']:.5f} GeV")
    print(f"  Gamma_Z           = {r['Gamma_Z_corr']:.5f} GeV")
    print(f"  R_b               = {r['R_b_corr']:.8f}")
    print(f"  R_l               = {r['R_l_corr']:.6f}")
    print(f"  sigma_had         = {r['sigma_had_corr_nb']:.6f} nb")
    print(f"  Delta_b top       = {r['delta_b']:.7f} ({r['delta_b']*100:.3f}%)")
    print(f"  sin2 theta_eff^l  = {r['sin2theta_eff_l']:.6f}")
    print("  formula check (SM inputs):")
    print(f"    M_W lead-univ = {fc['M_W_leading_universal']:.3f} GeV "
          f"(exp {fc['M_W_exp']:.3f})")
    print(f"    top vertex    = {fc['delta_b_pct']:.2f}%")
    print("ew_one_loop OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
