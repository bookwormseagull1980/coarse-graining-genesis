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

"""Source-explicit mass-action nuclear reaction networks.

Abundances are number per baryon, density is baryons/cm^3, and time is s.
An r-body directional rate coefficient has units cm^(3(r-1))/s, including
the thermal photon bath for photodissociation. Rates in molar units must
be converted before constructing a reaction. The mass-action convention
and factorial symmetry factors follow Serpico et al., JCAP 0412 (2004)
010, arXiv:astro-ph/0408076. This engine distributes no nuclear rate table
and does not invent a nuclear amplitude from the quark mass ladder.
Every rate must carry an explicit source and temperature validity range.
"""
from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Nuclide:
    name: str
    baryons: int
    charge: int

    def __post_init__(self):
        if (not self.name or not isinstance(self.baryons,int) or self.baryons<1
                or not isinstance(self.charge,int) or not 0<=self.charge<=self.baryons):
            raise ValueError("a named nuclide with integral A>=1 and 0<=Z<=A required")


@dataclass(frozen=True)
class NuclearReaction:
    """One direction; the inverse needs its own sourced coefficient.

    reactants/products are nonnegative integer multiplicity tuples aligned
    with the network's nuclides. coefficient(T_GeV) excludes density and
    symmetry factors. Photons are a bath and do not occupy a nuclide slot.
    """
    reactants: tuple
    products: tuple
    coefficient: object
    source: str
    temperature_range: tuple
    name: str


@dataclass(frozen=True)
class WeakConversion:
    """rate(t)->(lambda_n_to_p,lambda_p_to_n) in s^-1, with explicit source."""
    rate: object
    source: str


class ReactionNetwork:
    def __init__(self,nuclides,reactions):
        self.nuclides,self.reactions=tuple(nuclides),tuple(reactions)
        if not self.nuclides or len({n.name for n in self.nuclides})!=len(self.nuclides):
            raise ValueError("nonempty uniquely named nuclide list required")
        self.baryons=np.array([n.baryons for n in self.nuclides])
        charges=np.array([n.charge for n in self.nuclides])
        self.stoichiometry=[]
        for r in self.reactions:
            if not isinstance(r,NuclearReaction) or not callable(r.coefficient) or not r.source.strip():
                raise ValueError("each directional reaction needs a callable rate and explicit source")
            if len(r.reactants)!=len(self.nuclides) or len(r.products)!=len(self.nuclides):
                raise ValueError("stoichiometric dimensions do not match nuclides")
            if any(not isinstance(c,int) or c<0 for c in (*r.reactants,*r.products)) or not sum(r.reactants):
                raise ValueError("nonnegative integral multiplicities and at least one reactant required")
            low,high=r.temperature_range
            if not 0<low<high or not all(math.isfinite(t) for t in (low,high)):
                raise ValueError("positive finite temperature validity interval required")
            change=np.array(r.products)-np.array(r.reactants)
            if self.baryons@change!=0 or charges@change!=0:
                raise ValueError("nuclear reactions must conserve baryon number and charge")
            self.stoichiometry.append(change)

    def derivative(self,abundances,temperature,baryon_density):
        """Compute dY/dt for supplied bath data, without loading a rate database."""
        y=np.asarray(abundances,dtype=float)
        if y.shape!=(len(self.nuclides),) or not np.isfinite(y).all() or np.any(y<0):
            raise ValueError("finite nonnegative number-per-baryon abundances required")
        if not math.isfinite(baryon_density) or baryon_density<=0:
            raise ValueError("positive baryon density in cm^-3 required")
        result=np.zeros_like(y)
        for r,change in zip(self.reactions,self.stoichiometry):
            if not r.temperature_range[0]<=temperature<=r.temperature_range[1]:
                raise ValueError(f"temperature is outside the declared domain of {r.name}")
            rate=float(r.coefficient(temperature))
            if not math.isfinite(rate) or rate<0:
                raise ValueError("nonnegative finite directional rate coefficient required")
            flux=rate*baryon_density**(sum(r.reactants)-1)
            for yi,count in zip(y,r.reactants):
                flux*=yi**count/math.factorial(count)
            result+=change*flux
        return result

    def evolve(self,initial_abundances,time_interval,bath,*,weak_conversion=None,
               rtol=2e-7,atol=1e-11):
        """Stiff integration with bath(t)->(T_GeV,n_b_cm^-3).

        Tiny negative solver iterates are used only inside error tolerance;
        no final abundance is clipped or renormalized to conceal a residual.
        Nuclear rates determine abundances; this method makes no Yp=2Xn
        capture substitution. An explicit WeakConversion can evolve free
        n/p conversion throughout the nuclear evolution. Nuclear reactions
        conserve nuclear charge; this weak exchange transfers charge to the
        declared electron bath while preserving baryon number.
        """
        y0=np.asarray(initial_abundances,dtype=float)
        self.derivative(y0,*bath(time_interval[0]))
        if not np.isclose(self.baryons@y0,1,rtol=1e-10,atol=1e-12):
            raise ValueError("initial abundances must carry one baryon per baryon")
        if not time_interval[1]>time_interval[0] or min(rtol,atol)<=0:
            raise ValueError("increasing time interval and positive tolerances required")
        if weak_conversion is not None:
            if (not isinstance(weak_conversion,WeakConversion) or not callable(weak_conversion.rate)
                    or not weak_conversion.source.strip()):
                raise ValueError("weak conversion needs a rate callable and explicit source")
            names=[n.name for n in self.nuclides]
            if 'n' not in names or 'p' not in names:
                raise ValueError("weak conversion requires explicitly named n and p species")
            ni,pi=names.index('n'),names.index('p')
            if self.nuclides[ni]!=Nuclide('n',1,0) or self.nuclides[pi]!=Nuclide('p',1,1):
                raise ValueError("n and p species have inconsistent baryon/charge labels")
        def rhs(t,y):
            if np.min(y)<-100*atol:
                raise ArithmeticError("nuclear integrator left its positivity tolerance")
            positive=np.maximum(y,0)
            value=self.derivative(positive,*bath(t))
            if weak_conversion is not None:
                np_rate,pn_rate=weak_conversion.rate(t)
                if not all(math.isfinite(rate) and rate>=0 for rate in (np_rate,pn_rate)):
                    raise ValueError("nonnegative finite weak conversion rates required")
                net=np_rate*positive[ni]-pn_rate*positive[pi]
                value[ni]-=net
                value[pi]+=net
            return value
        solution=solve_ivp(rhs,time_interval,y0,method='Radau',rtol=rtol,atol=atol)
        if not solution.success:
            raise RuntimeError(solution.message)
        baryon_error=float(np.max(np.abs(self.baryons@solution.y-1)))
        if np.min(solution.y)<-10*atol or baryon_error>max(20*atol,10*rtol):
            raise ArithmeticError("network solution failed positivity or baryon conservation")
        return {"time_seconds":solution.t,"abundances":solution.y,
                "baryon_conservation_residual":baryon_error,
                "rate_sources":tuple(r.source for r in self.reactions),
                "nuclides":tuple(n.name for n in self.nuclides),
                "weak_source":None if weak_conversion is None else weak_conversion.source}
