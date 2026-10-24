"""Native coefficient composition and complete three-dimensional curvature.

All constants come from the existing (2,1) coexact source and SU(3) matter
matrices. The composition parameter is the coefficient Mehler parameter;
it is not assigned a conversion to a physical clock or a lepton propagator.
"""
from __future__ import annotations

from fractions import Fraction
import math


def _rising(x, n):
    result = Fraction(1)
    for j in range(n):
        result *= x+j
    return result


def _shape(dimension):
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("positive integer coefficient dimension required")
    return Fraction(dimension, 2)


def intensity_polynomial(degree, *, dimension):
    """Monic radial eigenpolynomial in x=N/q, in ascending powers of x."""
    alpha = _shape(dimension)
    if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
        raise ValueError("nonnegative integer degree required")
    return [(-1)**(degree-j)*Fraction(math.factorial(degree), math.factorial(j))
            *_rising(alpha+j, degree-j)/math.factorial(degree-j)/alpha**(degree-j)
            for j in range(degree+1)]


def intensity_generator(polynomial, *, dimension):
    """(L/(2*omega)) f=(1-x)f'+(2*x/M)f''; exact rational coefficients."""
    alpha = _shape(dimension)
    result = [Fraction(0)]*len(polynomial)
    for j, value in enumerate(map(Fraction, polynomial)):
        if j:
            result[j] -= j*value
            result[j-1] += (j+Fraction(j*(j-1))/alpha)*value
    return result


def intensity_update(polynomial, correlation_squared, *, dimension):
    """Exact conditional polynomial expectation inherited from the Gaussian update.

    r=rho^2=exp(-2*omega*h). This is the radial restriction of that
    update, not an independently chosen diffusion or stationary law.
    """
    alpha = _shape(dimension)
    r = Fraction(correlation_squared)
    if not 0 <= r <= 1:
        raise ValueError("squared coefficient correlation must lie in [0,1]")
    result = [Fraction(0)]*len(polynomial)
    for k, value in enumerate(map(Fraction, polynomial)):
        for j in range(k+1):
            result[j] += (value*math.comb(k, j)*_rising(alpha+j, k-j)
                          *((1-r)/alpha)**(k-j)*r**j)
    return result


def intensity_expectation(polynomial, *, dimension):
    alpha = _shape(dimension)
    return sum((Fraction(value)*_rising(alpha, k)/alpha**k
                for k, value in enumerate(polynomial)), Fraction(0))


def curvature_haar_constants():
    """Exact SO(3) Haar contractions of the generated vector addition kernel.

    K(R)=3/10*((Tr R)*R+R^2)-I/5. Its axial eigenvalue is
    a=(2+3*cos(theta))/5; the squared planar singular value is
    b=(17+21*cos(theta)+12*cos(theta)^2)/50.
    """
    def multiply(p, q):
        out = [Fraction(0)]*(len(p)+len(q)-1)
        for i, x in enumerate(p):
            for j, y in enumerate(q):
                out[i+j] += x*y
        return out

    def haar(p):
        def moment(k):
            if k % 2 == 0:
                return Fraction(math.comb(k, k//2), 2**k)
            return -Fraction(math.comb(k+1, (k+1)//2), 2**(k+1))
        return sum((x*moment(k) for k, x in enumerate(p)), Fraction(0))

    a = [Fraction(2, 5), Fraction(3, 5)]
    b = [Fraction(17, 50), Fraction(21, 50), Fraction(12, 50)]
    return {"determinant": haar(multiply(a, b)),
            "wedge_square": haar(multiply(b, b))+2*haar(multiply(multiply(a, a), b)),
            "norm_square": haar(multiply(a, a))+2*haar(b)}


def colour_source_response(native_gap):
    """Resolve the complete Q=||dB+B wedge B||^2 under its source composition.

    The supplied record must be the existing 15 spatial by 8 colour source.
    W2,W3,W4 are orthogonal Hermite-sector variances, not independent noise
    inputs. The fixed-mean partial Legendre curvature is negative residual
    susceptibility; it is not a second positive-field covariance.
    """
    M, h, cad = (native_gap[key] for key in
                 ("source_dimension", "algebra_dimension", "adjoint_casimir"))
    if (M, h, cad) != (120, 8, 3):
        raise ValueError("the generated (2,1) SU(3) source record is required")
    q, volume, lam = (float(native_gap[key]) for key in
                      ("intensity_q", "volume", "long_root_eigenvalue"))
    omega = lam+float(native_gap["transverse_shift"])
    if not all(math.isfinite(x) and x > 0 for x in (q, volume, lam, omega)):
        raise ValueError("finite positive generated source coordinates required")
    alpha = cad/(3*volume*h)
    W2 = 2*q*q/M*(lam+2*alpha*q)**2
    W3 = 7*cad*lam*q**3/(75*volume*h*h)
    W4 = 9*cad**2*q**4/(1250*volume**2*h**3)
    radial_W4 = 8*alpha**2*q**4/(M*(M+2))
    total = math.fsum((W2, W3, W4))
    radial = W2+radial_W4
    integral = math.fsum((W2/2, W3/3, W4/4))/omega
    radial_integral = (W2/2+radial_W4/4)/omega
    # Joint source continuation at the stationary intensity q:
    # Phi(n,J)=F(n)+Gamma(n,J)-Gamma(n,0), with W=log E exp(h*N-J*Q).
    # This static Schur response uses the existing collective Hessian. The
    # fixed-source Mehler rates in curvature_covariance remain unchanged.
    restoring = float(native_gap["potential_curvature"])
    radial_mass = float(native_gap["radial_mass_squared"])
    if not all(math.isfinite(x) and x > 0 for x in (restoring, radial_mass)):
        raise ValueError("positive finite collective curvature and radial mass required")
    variance = 2*q*q/M
    if not math.isclose(radial_mass, variance*restoring, rel_tol=2e-12):
        raise ValueError("radial mass and source information metric are inconsistent")
    mean_derivative = lam+2*alpha*q
    direct = math.fsum((W3, W4))
    collective = W2/radial_mass
    susceptibility = {
        "direct": direct,
        "collective": collective,
        "total": math.fsum((direct, collective)),
        "stationary_intensity_derivative_J": -mean_derivative/restoring,
        "mean_curvature_derivative_q": mean_derivative,
        "potential_curvature": restoring,
        "radial_mass_squared": radial_mass,
        "definition": "-d_J Gamma_J(n(J),J) at J=0+; partial_n Phi(n(J),J)=0",
        "continuation": "Phi(n,J)=F(n)+Gamma(n,J)-Gamma(n,0)",
    }
    constants = curvature_haar_constants()
    return {
        "source_dimension": M, "spatial_dimension": 3, "intensity_q": q,
        "coefficient_composition_rate": omega,
        "intensity_correlation_rate": 2*omega,
        "collective_law_tangent_restoring_rate": native_gap["radial_mass_squared"],
        "stationary_intensity_shape": M/2,
        "stationary_intensity_scale": 2*q/M,
        "intensity_variance": 2*q*q/M,
        "normalized_score_third_moment": math.sqrt(8/M),
        "normalized_score_fourth_moment": 3+12/M,
        "score_square_variance": 2+12/M,
        "centred_score_square_covariance_weights": {"rate_a": 8/M, "rate_2a": 2+4/M},
        "curvature_mean": lam*q+alpha*q*q,
        "curvature_Hermite_weights": {"degree_2": W2, "degree_3": W3, "degree_4": W4},
        "radial_fourth_weight": radial_W4,
        "angular_fourth_weight": W4-radial_W4,
        "curvature_variance": total, "radial_curvature_variance": radial,
        "full_to_radial_fourth_weight_ratio": W4/radial_W4,
        "omitted_fraction_of_full_variance": (W3+W4-radial_W4)/total,
        "full_variance_excess_over_radial": total/radial-1,
        "curvature_covariance_integral_composition_units": integral,
        "full_integral_excess_over_radial": integral/radial_integral-1,
        "fixed_mean_partial_legendre_curvature_JJ": -(W3+W4),
        "fixed_mean_residual_covariance_weights": {"degree_3": W3, "degree_4": W4},
        "joint_static_susceptibility": susceptibility,
        "haar_contractions": {key: str(value) for key, value in constants.items()},
        "covariance_definition": "sum_(d=2,3,4) W_d exp(-d*omega*abs(h))",
        "composition_clock_conversion_assigned": False,
        "lepton_mixed_vertex_assigned": False,
    }


def curvature_covariance(response, lag):
    lag = float(lag)
    if not math.isfinite(lag):
        raise ValueError("finite composition lag required")
    omega = response["coefficient_composition_rate"]
    return math.fsum(response["curvature_Hermite_weights"][f"degree_{d}"]
                     *math.exp(-d*omega*abs(lag)) for d in (2, 3, 4))


def curvature_laplace(response, parameter):
    """One-sided Laplace transform, in the unchanged composition units."""
    parameter = float(parameter)
    if not math.isfinite(parameter) or parameter < 0:
        raise ValueError("finite nonnegative Laplace parameter required")
    omega = response["coefficient_composition_rate"]
    return math.fsum(response["curvature_Hermite_weights"][f"degree_{d}"]
                     /(parameter+d*omega) for d in (2, 3, 4))
