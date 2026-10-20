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

"""Exact finite-content responses used in Guo (2026g), Appendix C.

The charged 15-component quotient is inherited from Guo (2026d). The
screening addition and its colour normalization remain the specified
Guo (2026g) readout. This module evaluates their joint compatibility; it
does not infer a generation count from an endpoint already using it.
"""
from fractions import Fraction as Q
import math

from cg_core.content_derivation import all_content

# The content is derived from the primitive charge lattice, not assigned as a
# table.  The neutral scalar-upper line (nu_R) is retained in the full carrier
# but excluded from the charged 15-coordinate quotient.
_CONTENT_ORDER = ("Q_L", "u_R", "d_R", "L_L", "e_R", "nu_R")
_CONTENT_BY_NAME = {row[0]: row for row in all_content()}
FULL_GENERATION = tuple(_CONTENT_BY_NAME[name] for name in _CONTENT_ORDER)
CHARGED_GENERATION = tuple(
    (name, reps, y, count, sign)
    for name, reps, y, count, sign in FULL_GENERATION if name != "nu_R"
)


def chiral_anomalies():
    """Exact LH-minus-RH coefficients; conventional common factors omitted."""
    rows = CHARGED_GENERATION
    return {
        "U1_cubed": sum(sign * n * y**3 for _, _, y, n, sign in rows),
        "gravity_U1": sum(sign * n * y for _, _, y, n, sign in rows),
        "SU3_squared_U1": sum(sign * rep[1] * y * Q(1, 2)
                              for _, rep, y, _, sign in rows if rep[0] == 3),
        "SU2_squared_U1": sum(sign * rep[0] * y * Q(1, 2)
                              for _, rep, y, _, sign in rows if rep[1] == 2),
        "SU3_cubed": sum(sign * rep[1]
                         for _, rep, _, _, sign in rows if rep[0] == 3),
        "SU2_doublet_parity": sum(rep[0] for _, rep, _, _, _ in rows
                                   if rep[1] == 2) % 2,
    }


def finite_source_response():
    """Gradient and connected Hessian of log Tr exp(u chi+vY+x.t)/15.

    Weak blocks are sigma_a/2 on each left doublet and zero on right
    singlets. Tr(t_a t_b)=number_of_doublets/2 delta_ab. Hypercharges
    are constant within each doublet, so the mixed weak traces vanish.
    All entries use exact rational arithmetic.
    """
    n = sum(row[3] for row in CHARGED_GENERATION)
    j = sum(c * sign for _, _, _, c, sign in CHARGED_GENERATION)
    y = sum(c * charge for _, _, charge, c, _ in CHARGED_GENERATION)
    y2 = sum(c * charge**2 for _, _, charge, c, _ in CHARGED_GENERATION)
    jy = sum(c * sign * charge for _, _, charge, c, sign in CHARGED_GENERATION)
    doublets = sum(rep[0] for _, rep, _, _, sign in CHARGED_GENERATION
                   if rep[1] == 2 and sign == 1)
    mean_j, mean_y = Q(j, n), y / n
    h = [[Q(0) for _ in range(5)] for _ in range(5)]
    h[0][0] = 1 - mean_j**2
    h[1][1] = y2 / n - mean_y**2
    h[0][1] = h[1][0] = jy / n - mean_j * mean_y
    for i in range(2, 5):
        h[i][i] = Q(doublets, 2 * n)
    return {"dimension": n, "gradient": (mean_j, mean_y, Q(0), Q(0), Q(0)),
            "hessian": tuple(tuple(row) for row in h),
            "hypercharge_second_moment": y2,
            "weak_extensive_per_generation": Q(doublets, 2),
            "tau": mean_j / (n * h[1][1]),
            "carrier_scope": "15-coordinate gauge-active charged quotient",
            "complete_carrier_dimension": 16,
            "complete_center_bias": Q(0)}


def chiral_center_response(log_left_right_ratio=0.0, *, neutral_right_weight=1.0):
    """Exact center response before and after neutral-right elimination.

    ``neutral_right_weight=1`` is the complete 16-coordinate carrier and
    ``neutral_right_weight=0`` is the charged 15-coordinate quotient.  Values
    between zero and one describe an explicitly retained effective weight;
    they are not silently identified with an exact Schur elimination.

    The optional argument is an applied response probe: half the logarithm
    of the left/right weight ratio.  It is not a source required by the
    closed generated carrier.  Differentiation with respect to the probe
    gives the connected center susceptibility.
    """
    if not math.isfinite(log_left_right_ratio):
        raise ValueError("a finite logarithmic left/right ratio is required")
    if not (math.isfinite(neutral_right_weight) and neutral_right_weight >= 0.0):
        raise ValueError("the neutral-right weight must be finite and nonnegative")
    left_capacity = 8.0
    charged_right_capacity = 7.0
    right_capacity = charged_right_capacity + neutral_right_weight
    applied_probe = 0.5 * log_left_right_ratio
    content_drive = 0.5 * math.log(left_capacity / right_capacity)
    total_drive = applied_probe + content_drive
    bias = math.tanh(total_drive)
    susceptibility = 1.0 - bias * bias
    return {
        "left_capacity": left_capacity,
        "charged_right_capacity": charged_right_capacity,
        "neutral_right_weight": neutral_right_weight,
        "right_capacity": right_capacity,
        "total_capacity": left_capacity + right_capacity,
        "applied_probe": applied_probe,
        "content_drive": content_drive,
        "total_drive": total_drive,
        "bias": bias,
        "susceptibility": susceptibility,
        "restoring_hessian": 1.0 / susceptibility,
        "complete_carrier": neutral_right_weight == 1.0,
        "charged_quotient": neutral_right_weight == 0.0,
        "removed_coordinate": None if neutral_right_weight == 1.0 else "nu_R",
        "elimination_feedback_required": neutral_right_weight != 1.0,
        "external_source_required": False,
    }


def closed_chiral_center_certificate():
    """Certify intrinsic center closure of the complete matter carrier.

    With eight left and eight right coordinates, the normalized partition
    function under an optional odd probe h is

        Z(h) = (8 exp(h) + 8 exp(-h))/16 = cosh(h).

    It is even, so its logarithmic derivative vanishes at h=0.  The charged
    15-coordinate quotient is returned only as a projection diagnostic; its
    8:7 offset is not an asymmetry of the complete generated system.
    """
    complete = chiral_center_response()
    quotient = chiral_center_response(neutral_right_weight=0.0)
    return {
        "complete_dimension": 16,
        "left_capacity": complete["left_capacity"],
        "right_capacity": complete["right_capacity"],
        "partition_at_zero": 1.0,
        "partition_even": True,
        "closed_center_bias": complete["bias"],
        "closed_center_susceptibility": complete["susceptibility"],
        "closed_restoring_hessian": complete["restoring_hessian"],
        "external_source_required": False,
        "quotient_dimension": 15,
        "quotient_bias": quotient["bias"],
        "quotient_is_projection_defect": True,
        "removed_coordinate": quotient["removed_coordinate"],
        "scope": (
            "intrinsic closure of the complete 8_L+8_R generated carrier; "
            "an applied probe is optional and belongs only to response theory"
        ),
    }


def closed_generated_world_contract():
    """Return the zero-argument contract of the complete generated world.

    Minimal unbiased compositional change is the sole ontological root.  The
    finite source, complete matter carrier, quotient responses, probes,
    subsystem boundaries, and comparison records are downstream realizations
    or readouts; none is a second dynamical cause.
    """
    center = closed_chiral_center_certificate()
    return {
        "sole_root": "minimal_unbiased_compositional_change",
        "root_argument_count": 0,
        "complete_matter_capacity": (
            center["left_capacity"] + center["right_capacity"]
        ),
        "complete_capacity_balanced": (
            center["left_capacity"] == center["right_capacity"]
            and center["closed_center_bias"] == 0.0
        ),
        "charged_quotient_is_internal_projection": center[
            "quotient_is_projection_defect"
        ],
        "applied_probes_are_response_coordinates": True,
        "subsystem_boundaries_are_internal_complements": True,
        "comparison_data_are_dynamical_sources": False,
        "external_dynamical_source_required": False,
    }


def chiral_center_power_law_screening(
    amplitude,
    exponent,
    *,
    scale_ratio=math.inf,
    neutral_right_weight=1.0,
):
    """Optional logarithmic-scale response to a decaying applied probe.

    For x=L/L0>=1, the applied probe is h(x)=amplitude*x**(-exponent).
    Since tanh is one-Lipschitz, with m0 the zero-drive content bias,

        |m(x)| <= |m0| + |amplitude| x**(-exponent).

    Integration against dx/x gives the returned finite-window bound.  On the
    infinite scale interval it is finite exactly in the balanced carrier
    covered here (m0=0); a nonzero quotient bias leaves a nonintegrable
    constant tail and is reported as such.  This diagnostic is not a closure
    premise: the complete carrier is already center balanced at zero probe.
    """
    if not (math.isfinite(amplitude) and math.isfinite(exponent) and exponent > 0.0):
        raise ValueError("finite amplitude and positive finite exponent required")
    if not (math.isinf(scale_ratio) or
            (math.isfinite(scale_ratio) and scale_ratio >= 1.0)):
        raise ValueError("scale_ratio must lie in [1,infinity]")
    source = chiral_center_response(
        0.0, neutral_right_weight=neutral_right_weight
    )
    baseline = abs(float(source["bias"]))
    magnitude = abs(float(amplitude))
    if math.isinf(scale_ratio):
        uniformly_integrable = baseline == 0.0
        upper_bound = magnitude * magnitude / (2.0 * exponent) if uniformly_integrable else math.inf
        zero_drive_energy = 0.0 if uniformly_integrable else math.inf
    else:
        log_span = math.log(scale_ratio)
        first_tail = (1.0 - scale_ratio ** (-exponent)) / exponent
        second_tail = (1.0 - scale_ratio ** (-2.0 * exponent)) / (2.0 * exponent)
        upper_bound = (
            baseline * baseline * log_span
            + 2.0 * baseline * magnitude * first_tail
            + magnitude * magnitude * second_tail
        )
        zero_drive_energy = baseline * baseline * log_span
        uniformly_integrable = True
    return {
        "amplitude": float(amplitude),
        "exponent": float(exponent),
        "scale_ratio": float(scale_ratio),
        "neutral_right_weight": float(neutral_right_weight),
        "baseline_bias": float(source["bias"]),
        "energy_upper_bound": upper_bound,
        "zero_drive_exact_energy": zero_drive_energy,
        "uniformly_integrable_on_declared_interval": uniformly_integrable,
        "infinite_scale_restoration": math.isinf(scale_ratio) and baseline == 0.0,
        "persistent_projection_defect": math.isinf(scale_ratio) and baseline != 0.0,
        "closure_input": False,
        "scope": (
            "complete-carrier chiral response; a neutral-state quotient must "
            "retain its Schur or threshold feedback separately"
        ),
    }


def finite_source_log_partition(u=0.0, v=0.0, x=(0.0, 0.0, 0.0)):
    """Independent finite block exponential, evaluated with log-sum-exp."""
    if len(x) != 3 or not all(math.isfinite(z) for z in (u, v, *x)):
        raise ValueError("finite five-coordinate source required")
    radius = math.hypot(*x)
    energies = []
    for _, rep, y, n, sign in CHARGED_GENERATION:
        base = sign * u + float(y) * v
        if rep[1] == 2:
            energies.extend([base + radius / 2] * rep[0])
            energies.extend([base - radius / 2] * rep[0])
        else:
            energies.extend([base] * n)
    high = max(energies)
    return high + math.log(math.fsum(math.exp(e-high) for e in energies) / len(energies))


def screening_compatibility(n_colours=3):
    """Solve delta_source(g)=2/(2g), n_colours*delta_source(g)=1.

    The four-doublet carrier used here is the inherited three-colour
    carrier. A changed colour representation requires a new calculation.
    """
    if n_colours != 3:
        raise ValueError("this certificate uses the inherited three-colour carrier")
    fermion_index = finite_source_response()["weak_extensive_per_generation"]
    g = Q(n_colours * 2, 1) / fermion_index
    if g.denominator != 1 or g <= 0:
        raise ValueError("no positive integral replication solves both prescriptions")
    return {"generations": int(g), "delta_source": Q(2, 1) / (g * fermion_index),
            "colour_residual": Q(n_colours * 2, 1) / (g * fermion_index) - 1,
            "premises": ("fixed charged one-generation carrier",
                         "extensive adjoint/fermion weak response ratio",
                         "colour screening normalization Nc*delta=1")}


def replicated_content(generations=None):
    """Instantiate selected charged content, or an explicitly diagnostic copy count."""
    g = screening_compatibility()["generations"] if generations is None else generations
    if not isinstance(g, int) or isinstance(g, bool) or g < 1:
        raise ValueError("a positive integer replication count is required")
    return tuple((f"{name}_g{copy+1}", rep, y, n, sign)
                 for copy in range(g) for name, rep, y, n, sign in CHARGED_GENERATION)


def charged_source_matrices():
    """Hermitian (chi,Y,t1,t2,t3) on the specified 15-coordinate carrier.

    The basis follows CHARGED_GENERATION, with a weak doublet for each
    colour. These are content-source matrices, not spatial kinetic terms.
    """
    import numpy as np
    pauli = (np.array([[0, 1], [1, 0]]),
             np.array([[0, -1j], [1j, 0]]), np.diag([1, -1]))
    result = np.zeros((5, 15, 15), dtype=complex)
    offset = 0
    for _, rep, charge, n, sign in CHARGED_GENERATION:
        sl = slice(offset, offset+n)
        result[0, sl, sl] = sign*np.eye(n)
        result[1, sl, sl] = float(charge)*np.eye(n)
        if rep[1] == 2:
            for a, sigma in enumerate(pauli):
                result[a+2, sl, sl] = np.kron(np.eye(rep[0]), sigma/2)
        offset += n
    return result


def log_partition_response(background, generators, source=None):
    """Value, gradient and Kubo--Mori Hessian of log Tr exp(K+J.A)/n.

    K and each A are finite Hermitian matrices. In the eigenbasis of K+J.A,
    the connected Hessian is sum_ij L(p_i,p_j) A^a_ij A^b_ji - <A^a><A^b>,
    with L the logarithmic mean. This Duhamel derivative accommodates
    noncommuting sources and reduces to an ordinary connected covariance
    for commuting generators and background. Exponential shifts and expm1 retain
    accuracy at repeated eigenvalues and at large spectral separations.
    """
    import numpy as np
    K = np.asarray(background, dtype=complex)
    A = np.asarray(generators, dtype=complex)
    if K.ndim != 2 or K.shape[0] != K.shape[1] or not K.shape[0]:
        raise ValueError("background must be a nonempty square matrix")
    n = K.shape[0]
    if A.ndim != 3 or A.shape[1:] != (n, n) or not len(A):
        raise ValueError("generators must have shape (sources, dimension, dimension)")
    J = np.zeros(len(A)) if source is None else np.asarray(source, dtype=float)
    if J.shape != (len(A),) or not all(np.isfinite(x).all() for x in (K,A,J)):
        raise ValueError("finite matrices and one real coordinate per generator required")
    if not np.allclose(K, K.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError("background must be Hermitian")
    if not np.allclose(A, A.conj().transpose(0,2,1), rtol=1e-12, atol=1e-13):
        raise ValueError("source generators must be Hermitian")
    energies, U = np.linalg.eigh(K+np.einsum('a,aij->ij', J,A))
    shifted = np.exp(energies-energies[-1])
    p = shifted/shifted.sum()
    rotated = np.einsum('ij,ajk,kl->ail', U.conj().T,A,U)
    gradient = np.einsum('i,aii->a',p,rotated).real
    delta = np.abs(energies[:,None]-energies[None,:])
    ratio = np.ones_like(delta)
    np.divide(-np.expm1(-delta), delta, out=ratio, where=delta!=0)
    mean = np.maximum(p[:,None],p[None,:])*ratio
    hessian = np.einsum('ij,aij,bji->ab',mean,rotated,rotated).real
    hessian -= np.outer(gradient,gradient)
    return {"log_partition":float(energies[-1]+np.log(shifted.sum()/n)),
            "gradient":gradient,"hessian":(hessian+hessian.T)/2,
            "probabilities":p,"dimension":n,
            "response":"connected Duhamel / Kubo-Mori finite-source Hessian"}


def interacting_content_response(background=None, source=None):
    """Evaluate the same five source coordinates at a supplied interaction K.

    tau_response is the declared gradient/Hessian readout at this K. Its
    zero-background value is 1/50; no invariance under arbitrary interactions
    is imposed. The charged-quotient modulus of finite_source_response stays
    separate from the zero center bias of the complete carrier.
    """
    import numpy as np
    A = charged_source_matrices()
    K = np.zeros((15,15)) if background is None else background
    result = log_partition_response(K,A,source)
    denominator = 15*result["hessian"][1,1]
    result["tau_response"] = (float(result["gradient"][0]/denominator)
                              if denominator > 0 else None)
    return result


def weighted_content_response(left_weight, right_weight):
    """Positive block weights implemented as K=log(w_L)P_L+log(w_R)P_R.

    A common multiplier cancels from every normalized response. Unequal
    weights change the charged-quotient response tau: for r=w_L/w_R it is
    (8r-7)/(10r+40). This does not define the complete-carrier center mean.
    """
    import numpy as np
    if not all(math.isfinite(w) and w > 0 for w in (left_weight,right_weight)):
        raise ValueError("strictly positive finite weights required")
    chi = charged_source_matrices()[0]
    K = (math.log(left_weight)*(np.eye(15)+chi)
         +math.log(right_weight)*(np.eye(15)-chi))/2
    return interacting_content_response(K)
