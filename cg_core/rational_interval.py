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

"""Small outward rational interval kernel on the grid 10**(-40).

Integer arithmetic controls rounding. Elementary enclosures follow
Guo (2026g) Appendix D: Machin's alternating pi series, integer square
roots, and a positive exponential Taylor polynomial with explicit tail.
No binary floating-point value enters a certified computation.
"""
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import factorial, isqrt

GRID = 10**40


def _ceil_div(a, b):
    return -((-a) // b)


@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @classmethod
    def point(cls, value):
        q = Fraction(str(value)) if isinstance(value, float) else Fraction(value)
        return cls(q.numerator * GRID // q.denominator,
                   _ceil_div(q.numerator * GRID, q.denominator))

    @classmethod
    def bounds(cls, lower, upper):
        return cls(cls.point(lower).lo, cls.point(upper).hi)

    def __add__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -(other if isinstance(other, Interval) else self.point(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        products = (self.lo*other.lo, self.lo*other.hi,
                    self.hi*other.lo, self.hi*other.hi)
        return Interval(min(products)//GRID, _ceil_div(max(products), GRID))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("interval contains zero")
        return Interval(GRID*GRID//self.hi, _ceil_div(GRID*GRID, self.lo))

    def __truediv__(self, other):
        other = other if isinstance(other, Interval) else self.point(other)
        return self * other.reciprocal()

    def __rtruediv__(self, other):
        return self.reciprocal() * other

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("nonnegative integer power required")
        out = Interval.point(1)
        base = self
        while n:
            if n % 2:
                out = out * base
            base = base * base
            n //= 2
        return out

    def sqrt(self):
        if self.lo < 0:
            raise ValueError("sqrt requires a nonnegative interval")
        lower = isqrt(self.lo * GRID)
        upper = isqrt(self.hi * GRID)
        if upper * upper != self.hi * GRID:
            upper += 1
        return Interval(lower, upper)

    def decimal_bounds(self, digits=16):
        """Decimal strings rounded outward, suitable for a saved certificate."""
        if not 0 <= digits <= 40:
            raise ValueError("decimal digits must lie in 0..40")
        step = 10**(40-digits)
        def render(n):
            sign = "-" if n < 0 else ""
            value = str(abs(n)).zfill(digits+1)
            return sign + (value[:-digits] + "." + value[-digits:] if digits else value)
        return [render(self.lo//step), render(_ceil_div(self.hi, step))]


@lru_cache(maxsize=1)
def pi_interval():
    def atan_inverse(n):
        partial = sum(((-1)**k * Fraction(1, (2*k+1)*n**(2*k+1))
                       for k in range(40)), Fraction(0))
        next_term = Fraction(1, 81*n**81)
        return Interval.bounds(partial, partial+next_term)
    return 16*atan_inverse(5)-4*atan_inverse(239)


@lru_cache(maxsize=1)
def _exp_remainder():
    return Interval.point(Fraction(243*5**61, factorial(61)))


def exp_negative(x):
    """Enclose exp(-x), x>=0, by range reduction and the proved tail."""
    if x.lo < 0:
        raise ValueError("nonnegative exponential argument required")
    halvings = 0
    while x.hi > 5*GRID:
        x = x/2
        halvings += 1
    # Horner form of sum_(k=0)^60 x^k/k!.
    polynomial = Interval.point(1)
    for k in range(60, 0, -1):
        polynomial = 1 + x*polynomial/k
    exponential = Interval(polynomial.lo,
                           polynomial.hi + _exp_remainder().hi).reciprocal()
    for _ in range(halvings):
        exponential = exponential*exponential
    return exponential
