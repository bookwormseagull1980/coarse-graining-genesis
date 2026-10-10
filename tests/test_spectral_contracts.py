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

"""Independent object, exact-source and enclosure checks; no store writes."""
from fractions import Fraction as Q
import math
from pathlib import Path
import sys

import mpmath as mp
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cg_core import rp3_spectrum as spectrum
from cg_core.content_response import (
    chiral_anomalies, finite_source_response, finite_source_log_partition,
    replicated_content, screening_compatibility,
)
from cg_core.rational_interval import Interval as I, pi_interval, exp_negative
from cg_core.sm_content import N_GENERATIONS, hypercharge_sum_cube
from cg_core.spectrum_loop import sm_fermion_fields, _spinor_parity
from cg_core.window_weights import scalar_vector_window_ratio
from cg_frg.generation.spectral_certificate import certify_endpoint
from cg_frg.ewsb.native_condensate import (
    restoring_response, restoring_derivative, solve_native_condensate,
    scalar_mass_tower, uniform_gap_budget, intensity_response_certificate,
    finite_joint_relative_potential, joint_native_source_response,
    solve_joint_native_condensate,
)


@pytest.mark.parametrize("n",range(8))
def test_spin_labels_have_exact_representation_dimension(n):
    jl,jr=spectrum.spinor_quantum_numbers(n)
    assert (2*jl+1)*(2*jr+1)==spectrum.spinor_multiplicity(n)
    assert jl-jr==.5


def test_signed_dirac_and_source_projections_are_distinct():
    signed=spectrum.dirac_modes(2,5)
    assert [math.copysign(1,row[1]) for row in signed]==[1,-1,1,-1,1,-1]
    full=spectrum.dirac_squared_modes(2,5)
    plus=spectrum.dirac_squared_modes(2,5,projection="P_plus")
    minus=spectrum.dirac_squared_modes(2,5,projection="P_minus")
    assert sorted(plus+minus)==full
    assert all(d*d==lam for (_,d,_),(_,lam,_) in zip(signed,full))
    assert _spinor_parity("Q_L1","chiral")==1
    assert _spinor_parity("u_R1","chiral")==0
    with pytest.raises(ValueError):
        _spinor_parity("u_R1","typo")


def test_genuine_tt_has_two_branches_and_explicit_operator_shift():
    rough=spectrum.true_tt_modes(1,8)
    shifted=spectrum.true_tt_modes(1,8,operator="K6")
    assert sum(row[3] for row in rough if row[2]==6)==10
    assert all(abs(row[0]-row[1])==2 for row in rough)
    assert all(b[2]-a[2]==12 for a,b in zip(rough,shifted))
    assert min(row[2] for row in spectrum.response_tensor_modes(1,4))==14
    assert spectrum.tt_modes(1,4)==spectrum.response_tensor_modes(1,4)
    assert scalar_vector_window_ratio()==7/4


def test_heat_a0_matches_actual_catalogue_without_fake_next_coefficients():
    value=spectrum.heat_kernel(1e-4,1,l_max=800)
    normalized=(4*math.pi*1e-4)**1.5*value["K"]
    assert abs(normalized/value["a0"]-1)<.002
    assert value["a0"]==7*math.pi**2
    assert value["a2"] is None and value["a4"] is None
    true_trace=sum(d*math.exp(-1e-4*lam)
                   for _,_,lam,d in spectrum.true_tt_modes(1,800))
    assert abs((4*math.pi*1e-4)**1.5*true_trace/(2*math.pi**2)-1)<.002


def test_exact_finite_source_and_chiral_anomalies():
    result=finite_source_response()
    assert result["gradient"][0]==Q(1,15)
    assert [result["hessian"][i][i] for i in range(5)]==[
        Q(224,225),Q(2,9),Q(2,15),Q(2,15),Q(2,15)]
    assert result["tau"]==Q(1,50)
    assert all(value==0 for value in chiral_anomalies().values())
    assert math.isclose(hypercharge_sum_cube(),-4/9)
    h=1e-3
    for axis in range(5):
        coords=[0.0]*5
        coords[axis]=h
        plus=finite_source_log_partition(coords[0],coords[1],coords[2:])
        coords[axis]=-h
        minus=finite_source_log_partition(coords[0],coords[1],coords[2:])
        assert abs((plus+minus)/h**2-float(result["hessian"][axis][axis]))<2e-7


def test_screening_selection_precedes_content_instantiation():
    selection=screening_compatibility()
    assert selection["generations"]==N_GENERATIONS==3
    assert selection["colour_residual"]==0
    assert sum(row[3] for row in replicated_content())==45
    assert sum(field.n_components for field in sm_fermion_fields())==45
    for g in (1,2,4,10):
        assert Q(3,g)!=1


def test_elementary_enclosures_against_independent_high_precision_values():
    with mp.workdps(80):
        lo,hi=map(mp.mpf,pi_interval().decimal_bounds(39))
        assert lo<mp.pi<hi
        for x in (Q(0),Q(1,7),Q(5),Q(125,3)):
            low,high=map(mp.mpf,exp_negative(I.point(x)).decimal_bounds(39))
            exact=mp.exp(-mp.mpf(x.numerator)/x.denominator)
            assert low<=exact<=high
        low,high=map(mp.mpf,I.point(2).sqrt().decimal_bounds(39))
        assert low<mp.sqrt(2)<high


def test_r5_certificate_encloses_independent_adaptive_integrals():
    from scipy.integrate import quad
    result=certify_endpoint(1024)
    rows=[(0,.75,4),(8,.75,36),(4,1.5+1/15000,192),
          (4,1+1/15000,72),(4,1/15000,24),
          (9/4,3/20000,3*56),(25/4,3/20000,3*192),(49/4,3/20000,3*336)]
    center=27/(128*math.pi**3)*sum(d*quad(
        lambda u:((u*u+a)/(u*u+a+b))**2*math.exp(-(u*u+a)/math.pi),
        0,math.sqrt(5*math.pi-a),epsabs=1e-12)[0] for a,b,d in rows)
    lo,hi=map(float,result["endpoint"])
    assert lo<center<hi
    assert result["unique_positive_root"]
    assert result["three_position_platform_certified"]


@pytest.mark.parametrize("z",[0,1e-10,.1,.25,.250000001,2,50])
def test_full_conformal_response_matches_independent_infinite_sum(z):
    with mp.workdps(40):
        zz=mp.mpf(str(z))
        if zz<mp.mpf('.25'):
            b=mp.sqrt(mp.mpf('.25')-zz)
            exact=mp.pi/8-mp.pi*b/4*mp.tan(mp.pi*b/2)
        elif zz==mp.mpf('.25'):
            exact=mp.pi/8
        else:
            s=mp.sqrt(zz-mp.mpf('.25'))
            exact=mp.pi/8+mp.pi*s/4*mp.tanh(mp.pi*s/2)
        assert math.isclose(restoring_response(z),float(exact),rel_tol=2e-7,abs_tol=1e-14)
        derivative=mp.nsum(lambda j:(2*j+1)**2/((2*j+1)**2-mp.mpf('.25')+zz)**2,[0,mp.inf])
        assert math.isclose(restoring_derivative(z),float(derivative),rel_tol=2e-10)


def test_native_complete_root_and_mass_have_positive_tail_enclosures():
    result=solve_native_condensate(g="1",Z="2",L="2.5",shells=128,iterations=55)
    root=result["full_response_estimate"]["z"]
    mass=result["full_response_estimate"]["mass_squared"]
    zlo,zhi=map(float,result["z"])
    mlo,mhi=map(float,result["mass_squared"])
    assert 0<zlo<root<zhi
    assert 0<mlo<mass<mhi
    assert scalar_mass_tower(mass,2.5)[0]==(0,mass,1)
    nu=float(result["drive_nu"][0])
    assert abs(restoring_response(root)-nu)<1e-14
    intensity=intensity_response_certificate("0.1",
        amplitude_squared=I.bounds(*result["amplitude_squared"]),
        mass_squared=I.bounds(*result["mass_squared"]),Z="2",L="2.5")
    assert intensity["strict_positive_atom_certified"]
    assert intensity["infinite_internal_tail_included"]
    assert float(intensity["pole_mass_squared"][0])>0
    assert float(intensity["continuum_threshold_squared"][0])>mhi
    assert solve_native_condensate(g="1",Z="1",L="1")["phase"]=="uncondensed"


def test_uniform_native_gap_requires_explicit_positive_parameter_box():
    result=uniform_gap_budget(nu_bounds=("0.01","0.02"),
                              kappa_bounds=("2","3"),Z_bounds=("1","2"),shells=100)
    assert float(result["uniform_positive_gap_lower"])>0
    assert result["verified_input_box_required"]
    with pytest.raises(ValueError):
        uniform_gap_budget(nu_bounds=(0,1),kappa_bounds=(1,2),Z_bounds=(1,2),shells=100)


def test_joint_radius_square_completion_matches_original_finite_potential():
    # Evaluate the original spectral logarithm independently at points away
    # from its stationary radius and amplitude, including the zero boundary.
    with mp.workdps(50):
        for amplitude_squared, radius, coupling in ((0., 1.4, .9), (.07, 2.1, 1.3),
                                                    (.23, 3.4, .6)):
            result = finite_joint_relative_potential(
                amplitude_squared=amplitude_squared, L=radius, g=coupling, shells=7)
            y, L, g = map(lambda value: mp.mpf(str(value)),
                          (amplitude_squared, radius, coupling))
            direct = 8*(1/L**2-1/mp.pi)*y
            for j in range(8):
                dimension = (2*j+1)**2
                eigenvalue = (dimension-mp.mpf('.25'))/L**2
                deformation = g*y/eigenvalue
                direct += dimension*(deformation-mp.log1p(deformation))
            assert result['direct_potential'] == pytest.approx(float(direct), rel=3e-13, abs=2e-14)
            assert result['completed_square_potential'] == pytest.approx(float(direct), rel=3e-13, abs=2e-14)
            assert result['identity_residual'] == pytest.approx(0., abs=2e-14)
    # At fixed u=g L² y the completed square gives a strict global radius
    # minimum. This comparison changes y with L and is distinct from a
    # fixed-amplitude radial variation.
    u, coupling = .2, .8
    selected = math.sqrt(2*math.pi)
    minimum = finite_joint_relative_potential(
        amplitude_squared=u/(coupling*selected**2), L=selected, g=coupling, shells=7)
    for radius in (selected/2, selected*.9, selected*1.1, selected*2):
        value = finite_joint_relative_potential(
            amplitude_squared=u/(coupling*radius**2), L=radius, g=coupling, shells=7)
        difference = value['direct_potential']-minimum['direct_potential']
        expected = 8*u/coupling*(1/radius**2-1/(2*math.pi))**2
        assert difference == pytest.approx(expected, rel=4e-12, abs=2e-14)
        assert difference > 0


def test_joint_native_source_force_and_hessian_retain_both_variations():
    y, radius, coupling = .13, 2.8, .9
    result = joint_native_source_response(amplitude_squared=y, L=radius, g=coupling)
    # Independent convergent spectral derivatives include the j=0 mode
    # and differentiate at fixed amplitude when taking the volume source.
    with mp.workdps(40):
        yy, LL, gg = map(lambda value: mp.mpf(str(value)), (y, radius, coupling))
        z, kappa = 1/LL**2, gg*LL**2
        u = kappa*yy
        response = mp.nsum(lambda j: (2*j+1)**2*u/
                           (((2*j+1)**2-mp.mpf('.25'))*
                            ((2*j+1)**2-mp.mpf('.25')+u)), [0, mp.inf])
        slope = mp.nsum(lambda j: (2*j+1)**2/
                        ((2*j+1)**2-mp.mpf('.25')+u)**2, [0, mp.inf])
        expected_y = 8*(z-1/mp.pi)+kappa*response
        expected_eta = 16*z*yy-2*u*response
        expected_hessian = [[32*z*yy+4*u*response+4*u*u*slope,
                             16*z-2*kappa*(response+u*slope)],
                            [16*z-2*kappa*(response+u*slope), kappa*kappa*slope]]
        assert result['Fy'] == pytest.approx(float(expected_y), rel=3e-13, abs=2e-14)
        assert result['Feta'] == pytest.approx(float(expected_eta), rel=3e-13, abs=2e-14)
        for i in range(2):
            for j in range(2):
                assert result['hessian_eta_y'][i][j] == pytest.approx(
                    float(expected_hessian[i][j]), rel=3e-13, abs=2e-14)
        expected_relaxed = expected_hessian[0][0]-expected_hessian[0][1]**2/expected_hessian[1][1]
        assert result['relaxed_eta_curvature'] == pytest.approx(float(expected_relaxed), rel=3e-13, abs=2e-14)


def test_joint_native_equilibrium_has_certified_radius_and_positive_joint_hessian():
    result = solve_joint_native_condensate(g='1', Z='2', shells=64, iterations=50)
    radius_low, radius_high = map(float, result['selected_radius'])
    squared_low, squared_high = map(float, result['radius_squared'])
    # Decimal certificates are checked at high precision, rather than
    # requiring their binary64-rounded endpoints to remain distinct.
    with mp.workdps(60):
        low, high = map(mp.mpf, result['selected_radius'])
        assert low < mp.sqrt(2*mp.pi) < high
        low, high = map(mp.mpf, result['radius_squared'])
        assert low < 2*mp.pi < high
    assert radius_low == pytest.approx(math.sqrt(2*math.pi), rel=3e-16)
    assert radius_high == pytest.approx(math.sqrt(2*math.pi), rel=3e-16)
    assert squared_low == pytest.approx(2*math.pi, rel=3e-16)
    assert squared_high == pytest.approx(2*math.pi, rel=3e-16)
    assert result['stationary']['strict_positive_gap_certified']
    root = result['stationary']['full_response_estimate']['z']
    source = joint_native_source_response(
        amplitude_squared=root/(2*math.pi), L=math.sqrt(2*math.pi), g=1.)
    assert abs(source['Fy']) < 3e-13
    assert abs(source['Feta']) < 3e-13
    assert restoring_response(root) == pytest.approx(2/math.pi**2, rel=2e-13)
    hessian = source['hessian_eta_y']
    assert hessian[0][0] > 0 and hessian[1][1] > 0
    assert hessian[0][0]*hessian[1][1]-hessian[0][1]**2 > 0
    expected_relaxed = 64*(root/(2*math.pi))/(2*math.pi)
    assert source['relaxed_eta_curvature'] == pytest.approx(expected_relaxed, rel=3e-13)
    low, high = map(float, result['relaxed_eta_curvature'])
    assert 0 < low <= expected_relaxed <= high
    for enclosure in result['joint_hessian_u_z_diagonal']:
        assert float(enclosure[0]) > 0


def test_intensity_bubble_matches_independent_two_particle_dispersion():
    result=intensity_response_certificate("1",amplitude_squared="0.2",
        mass_squared="0.5",Z="2",L="2.5",shells=2,terms=48)
    with mp.workdps(60):
        z,m2,Z,L=map(mp.mpf,("1","0.5","2","2.5"))
        reference=mp.mpf(0)
        for j in range(3):
            a=m2+4*j*(j+1)/L**2
            # Independent dispersion integral of the two-particle phase space.
            reference+=(2*j+1)**2*mp.quad(
                lambda s:mp.sqrt(1-4*a/s)*z*z/(s*s*(s+z)),
                [4*a,8*a,mp.inf])/(8*mp.pi**2*Z**2)
        lo,hi=map(mp.mpf,result["finite_continuum_response"])
        assert lo<reference<hi
        assert result["pole_residue"]==["0.40000000000000000000000000000000"]*2


def test_intensity_infinite_tail_and_zero_condensate_visibility():
    coarse=intensity_response_certificate("1",amplitude_squared="0",
        mass_squared="0.5",Z="2",L="2.5",shells=2,terms=48)
    fine=intensity_response_certificate("1",amplitude_squared="0",
        mass_squared="0.5",Z="2",L="2.5",shells=32,terms=48)
    assert not coarse["strict_positive_atom_certified"]
    assert float(coarse["pole_residue"][1])==0
    assert float(fine["continuum_tail_upper"])<float(coarse["continuum_tail_upper"])
    with mp.workdps(50):
        m2,L=mp.mpf(".5"),mp.mpf("2.5")
        # The positive bubble is at most z²/(60*a²) before its common prefactor.
        exact_square_tail=mp.nsum(lambda j:(2*j+1)**2/
            (m2+4*j*(j+1)/L**2)**2,[3,mp.inf])
        independent_bound=exact_square_tail/(480*mp.pi**2*4)
        assert independent_bound<mp.mpf(coarse["continuum_tail_upper"])
        low=mp.mpf(fine["subtracted_response"][0])
        high=mp.mpf(fine["subtracted_response"][1])
        assert mp.mpf(coarse["subtracted_response"][0])<low
        assert high<mp.mpf(coarse["subtracted_response"][1])


@pytest.mark.parametrize("changes",[
    {"mass_squared":"0"},{"Z":"0"},{"shells":-1},{"terms":3},
    {"Q_squared":"5"},{"external_kinetic":"unspecified"},
])
def test_intensity_certificate_requires_its_stated_action_and_series_domain(changes):
    inputs=dict(Q_squared="1",amplitude_squared=".2",mass_squared="1",
                Z="2",L="2.5",shells=2,terms=24)
    inputs.update(changes)
    with pytest.raises(ValueError):
        intensity_response_certificate(**inputs)
