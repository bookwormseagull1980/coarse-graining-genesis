<!--
Coarse-Graining Genesis Framework V5.0
Author: Jinku Guo <guojk@nwpu.edu.cn>
Northwestern Polytechnical University, Xi'an 710072, China
ORCID: 0009-0000-6600-6171
References:
Guo, J. (2026a). Certified Spectral Computation for Semilinear Evolution: Finite Records and Polynomial Bit Cost. Unpublished manuscript.
Guo, J. (2026b). Coarse-Graining and Long-Range Response in Generated Systems. Unpublished manuscript.
Guo, J. (2026c). Dynamics of Generated Spectra from Minimal Change: Certified Function Classes and Finite Windows. Unpublished manuscript.
Guo, J. (2026d). The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap. Unpublished manuscript.
Guo, J. (2026e). A Spectral Construction of Natural-Number Arithmetic. Unpublished manuscript.
Guo, J. (2026f). A Spectral Criterion for Emergent Gravity. Unpublished manuscript.
Guo, J. (2026g). The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales. Unpublished manuscript.
Guo, J. (2026h). The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation. Unpublished manuscript.
Full bibliography: REFERENCES.md and CITATION.cff.
-->

# V5 Verification Report

Generated: 2026-10-18 09:22:30
Python: `3.12.10`
Root: `.`

## Verdict

PASS for the executed checks

A requested reproduction builds empty temporary stores and publishes only after success.
The results below identify the checks executed in this invocation;
a proof-library result does not certify a numerical run or the entire manuscript chain.

## Not Executed

- Lean archive compilation (source audit alone is not compilation).
- Lean Formalization of Arithmetic and Basic Physical Interfaces compilation and axiom audit (enable with --foundations).
- Isolated full-chain numeric stability rerun (enable with --stability).

No PASS claim is made for these omitted checks.

## Steps

| step | status | command |
|---|---:|---|
| full reproduction | PASS | `python -B scripts/reproduce_v5.py` |
| current run manifest | PASS | `verify existing run identity and fingerprints` |
| parameter provenance audit | PASS | `python scripts/audit_param_writers.py` |
| observation leakage audit | PASS | `python scripts/audit_observation_leakage.py` |
| Lean source audit | PASS | `python scripts/audit_lean_sources.py` |
| numeric precision audit | PASS | `python scripts/audit_numeric_precision.py` |
| path portability audit | PASS | `python scripts/audit_path_portability.py` |
| full comparison table | PASS | `python comparison/param_audit_full.py` |
| pytest | PASS | `python -B -m pytest -q -m 'not release_audit' -p no:cacheprovider --basetemp <temporary>` |
| run identity after verification | PASS | `verify existing run identity and fingerprints` |

Full Python test results: 583 passed, 5 deselected, 10 subtests passed.
The complete release audits are executed in the steps above;
their duplicate test wrappers are deselected.

Audits executed once during reproduction and reused after current-run fingerprint validation: parameter provenance audit, observation leakage audit.

Run identity: `20261018T011955Z-546661b7`.
Bound calculation sources: 118; verification sources: 47; outputs: 2; reference identities: 99; solver execution identities: 2.

### Store Summary

- cg_params records: 241
- Isolated reference records: 99
- provenance: DERIVED=237, OBSERVED=1, PENDING=2, SCALE_CHOICE=1
- roles: anchor=1, cg=23, comparison=49, informational=21, internal=147
- declared physical definitions: 120
- declared direct-input sets: 122

### Selected Closed Values

| key | value | provenance | writer |
|---|---:|---|---|
| `kL` | `2.4935343325226915` | DERIVED | `cg_frg/frg/endpoint_constraint.py` |
| `M_G` | `1.7310765000475023e+18` | DERIVED | `cg_frg/frg/endpoint_constraint.py` |
| `g2_MG` | `0.5088477031823814` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `g1_MG_geo` | `0.6049900729523602` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `g3_MG_geo` | `0.4977601563548794` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `n_generations` | `3` | DERIVED | `cg_frg/generation/window_capacity.py` |
| `v_HIGGS` | `246.18969645238943` | DERIVED | `cg_frg/ewsb/vev_closure.py` |
| `M_Z_pred` | `91.12483998892056` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `M_W_pred` | `80.37174514486661` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `M_W_pred_lead1loop` | `80.33739698310175` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `Gamma_b_pred_1loop` | `0.38040730308009635` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `Gamma_had_pred_lead1loop` | `1.7520580283558593` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `Gamma_Z_pred_lead1loop` | `2.5063559621245686` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `R_b_pred_lead1loop` | `0.2171202648105626` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `R_l_pred_lead1loop` | `20.791529232604695` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `sigma_had_pred_lead1loop` | `41.54847835413312` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `sin2_theta_eff_l_pred` | `0.23011353985028052` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `m_H_pred` | `124.98344026878286` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `Omega_Lambda` | `0.6850442965140158` | DERIVED | `cg_frg/cosmology/dark_energy.py` |
| `Omega_Sigma` | `0.2655475114476184` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `T_CMB_GeV` | `2.353400743797703e-13` | DERIVED | `cg_frg/cosmology/dark_energy.py` |
| `T_CMB_corrected_K` | `2.725473977921092` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `endpoint_sigma8` | `None` | PENDING | `cg_frg/cosmology/endpoint_residual.py` |
| `endpoint_S8` | `None` | PENDING | `cg_frg/cosmology/endpoint_residual.py` |
| `bbn_dm_np` | `0.0012849675512388058` | DERIVED | `cg_frg/cosmology/bbn_helium.py` |
| `bbn_tau_n` | `915.5435125712569` | DERIVED | `cg_frg/cosmology/bbn_helium.py` |
| `bbn_Yp` | `0.2460823786548142` | DERIVED | `cg_frg/cosmology/bbn_helium.py` |
| `bbn_Neff` | `3.043873359487886` | DERIVED | `cg_frg/cosmology/bbn_helium.py` |

## Exact affine certificates

The following certificates refer to the explicitly supplied rational
matrices. Exact elimination verifies the kernel, slope and source overlap.
Physical tensor identification specifies the sourced action,
external momentum, constraints and polarization space.

| example | dimension | kernel dimension | visible rank | exact residue |
|---|---:|---:|---:|---|
| positive_mass | 2 | 0 | 0 | `[['0']]` |
| source_invisible_kernel | 2 | 1 | 0 | `[['0']]` |
| visible_kernel | 2 | 1 | 1 | `[['1/2']]` |

## Fixed compact branch

The undeformed ladder has x(0)=0.100656318445 and 1-x(0)=0.899343681555.
Its analytic denominator margin exceeds the exact rational bound `10043/172543`.
The radius and detuning are evaluated by A_R/c=4/27 and x(chi_c)=1.
For chi(Q^2)=chi_c-a Q^2+O(Q^4), a>0, the matched scalar
propagation residue is J(chi_c)/(c^4 a x'(chi_c)).
The external branch and its slope are determined from the sourced propagation action.

## External gauge-tensor realization

The specified quadratic Fierz-Pauli action has two physical helicities.
Its exact reduced kernel is Z Q^2 I_2; the source residue is g^2/Z.
The scope is the quadratic gauge action with leading conserved-source exchange.
Inverse-response matching to the compact ladder fixes the critical coordinate
and the external momentum conversion on the matched branch.

- Z = 5.930801014927169e+36 GeV^2
- residue = 1.686112883374625e-37 GeV^-2
- G = 6.708829999999999e-39 GeV^-2
- chi(0) = 0.6572248464344095
- -dchi/d(Q^2/M_P^2) = 0.1081571290582262

| Q^2/M_P^2 | chi | momentum times response | spectral evaluations |
|---:|---:|---:|---:|
| 0.0001 | 0.6572140305755785 | 0.999999999799943 | 6 |
| 1e-05 | 0.6572237648616597 | 1.000000000063828 | 6 |

### Classical tensor and matter completion

Einstein--scalar on one metric; covariant matter functionals use the same Hilbert source
g_metric=eta-2*g*Phi; M_star^2=Z/g^2
classical local two-derivative effective action
The arbitrary-field Noether identity is proved in Guo (2026f).
The exact local field-derivative checks evaluate that identity
and its field-amplitude coefficients for specified rational data.
They include a nonzero missing-cubic-vertex control.
These checks concern the macroscopic classical effective action,
its collective tensor response and conserved-source coupling.
Local Ward checks passed: True

## Canonical internal matter-source dynamics

finite canonical internal conformal matter source; occupied classical ensemble
L=(dot_phi^dagger M dot_phi-phi^dagger B phi)/2; M=exp(-3 eta); B=exp(-eta/2) A exp(-eta/2)
The source histories use the same operator, occupations and compression profiles
as the static matter response. Both frequency branches and their correlations
enter the causal response, including the direct second source variation.

- source-charge relative residual: 1.91480936223e-16
- causal-equation relative residual: 1.90973710345e-16
- response cutoff comparison: 7.04460217705e-16
- maximum canonical-form residual: 5.38626232194e-15
- maximum source-work balance residual: 1.16573417586e-14
- dominant operation counts: {'causal_entry_divisions': 1192464, 'dense_liouvillian_factorizations': 0, 'exact_segment_propagators': 6, 'nonzero_source_diagonalizations': 2, 'nonzero_source_mode_diagonalizations': 2, 'phase_response_basis_transforms': 0, 'reference_mode_diagonalizations': 2, 'retained_phase_dimensions': [140, 336]}

The exact finite source protocol has positive matter kinetic and spatial forms.
The external gravitational response additionally requires the collective metric
source map and the reduction of its common constraints.

### Clock parametrization of the same source history

d(proper time)=clock_rate*d(parameter) on each source segment
selected monotone parametrization of the same source history
- relative phase-covariance residual: 0
- source-work residual: 0
- additional source-family evaluations: 0
- reused source families: 3
- additional exact propagators: 3

## Covariant native source and metric constraints

finite internal matter coupled to an external metric and scalar compression sources
S_m=-integral sqrt(-g) [g^{mu nu} partial_mu(phi)^dagger M partial_nu(phi)+phi^dagger B phi]/2
nabla_mu T^mu_nu=Re(E_phi^dagger partial_nu phi)+Q_a partial_nu eta^a

- stress-divergence residual: 3.46944695195e-17
- normal stress / lapse-source residual: 0
- momentum stress / shift-source residual: 3.68807269888e-17
- source-work charge residual: 2.3966823025e-16
- Legendre-transform residual: -4.4408920985e-16
- dominant operation counts: {'common_source_diagonalizations': 1, 'exponential_frechet_divided_difference_matrices': 2, 'external_metric_inversions': 1, 'finite_difference_derivatives': 0, 'source_frechet_directions_per_matrix': 3, 'spatial_metric_inversions': 1}

The source and matter equations enter the total covariant conservation law.
The uniform canonical dilation retains its mixed velocity form and primary constraint.

### Generated matter-phase congruence

The complex coordinate pairs two existing equal-mass real directions of the same carrier.
The polar equations determine its unit flow, stress, source exchange and acceleration remainder.
Maximum residuals: {'acceleration_kinematics': 1.734723475976807e-18, 'clock_acceleration_identity': 1.734723475976807e-18, 'complex_field_equation': 6.245004513516506e-17, 'complex_source': 5.551115123125783e-17, 'complex_stress': 6.591949208711867e-17, 'normalization': 2.220446049250313e-16, 'phase_clock_rate': 1.1102230246251565e-16, 'phase_current': 2.7755575615628914e-17, 'pressure_acceleration': 3.469446951953614e-18, 'proper_time_rate': 2.220446049250313e-16, 'radial_equation': 5.551115123125783e-17, 'radial_gradient': 1.3877787807814457e-17, 'source_decomposition': 7.28583859910259e-17, 'stress_decomposition': 3.2959746043559335e-17}
Operation counts: {'additional_polar_jet_evaluations_for_clocks': 0, 'clock_covector_exterior_derivatives': 3, 'independent_complex_jet_evaluations': 3, 'local_polar_jet_evaluations': 3, 'time_evolution_steps': 0}

The local cases include a static accelerated phase, homogeneous expansion and a nonzero radial-pressure gradient.
Their existing field derivatives also determine the proper-time phase rate and the exterior derivative of the clock one-form.
Closure of that one-form supplies the local unit-gradient dust clock; the accelerated case retains proper time along each curve.

- homogeneous_expansion: phase rate = 0.68370726287; maximum clock exterior-derivative component = 0
- static_rest_phase: phase rate = 0.68370726287; maximum clock exterior-derivative component = 0.125
- varying_quantum_pressure: phase rate = 0.648621661041; maximum clock exterior-derivative component = 0.0122751504653

## Generated Fermi-input matching

The same generated weak input is represented in the tadpole-free
Landau-gauge MSbar VEV convention through one loop.
Six stored readouts supply the leading couplings and reference scale;
the finite coefficient is evaluated once without additional RG evolution.

- Q = 91.12483998892056 GeV
- v_F = 246.1896964523894 GeV
- G_F = 1.166662548042236e-05 GeV^-2
- v_L = 248.6618895442452 GeV
- v_L squared = 61826.623573031 GeV^2
- Delta r = 0.02008364385252736
- one-loop tadpole term = -375.7115102984538 GeV^2

The VEV and its square are separately truncated series.
Finite native-source readout corrections retain their source-matching definitions.

## Charged-lepton finite matching

The generated masses define three pole conditions of the common electroweak action.
The photon, W, Z and Higgs terms retain finite charged-lepton masses.
- matching scale: 91.12483998892056 GeV
- weighted one-loop correction: 0.00933751775404148
- finite weak part: 2.348914726193714e-06
- numerical interval: [0.009337517754041479, 0.009337517754041482]
- work: {'analytic_interval_B_evaluations': 9, 'distinct_A_values': 6, 'distinct_B_values': 9, 'quadrature_integrand_evaluations': 0}
- uncomputed orders: two-loop electroweak and QED corrections; neutrino-mass contributions

The interval encloses numerical evaluation at fixed input values; the perturbative remainder is separate.

- required weighted matching: 0.01127358296141212
- reference standard uncertainty: 0.0005816838843775095
- required minus predicted at the reference scale: 0.001936065880283619

The comparison retains the uncomputed perturbative remainder; no theory significance is assigned.

## Common neutron and helium comparison

S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024), neutron listing; registered helium benchmark

| quantity | calculated | reference | central residual (%) |
|---|---:|---:|---:|
| neutron_proton_mass_difference (GeV) | 0.00128496755124 | 0.00129333236 | -0.646764 |
| free_neutron_lifetime (s) | 915.543512571 | 878.4 | +4.22854 |
| helium_baryon_fraction (1) | 0.246082378655 | 0.245 | +0.441787 |

The shared-input Jacobian propagates independently supplied covariance or interval errors.
Operation counts: {'center_integrand_evaluations': 567, 'derivative_integrand_evaluations': 576, 'derivative_interval_evaluations': 16, 'finite_difference_chain_evaluations': 0, 'freeze_root_iterations': 120, 'phase_space_integrand_evaluations': 1143, 'phase_space_quadratures': 1, 'reused_center_subintervals': 14}

No joint significance is assigned without the weak-rate and hadronic theory covariance.

### Independent QCD+QED comparison

independent QCD+QED total at its physical point; generated weak and thermal inputs retained

| input variation | mass difference (GeV) | lifetime (s) | helium fraction |
|---|---|---|---|
| additive_envelope | [0.00112, 0.0019000000000000002] | [86.20276246216451, 2330.923327112371] | [0.009830736984774179, 0.3552893137328956] |
| statistical | [0.00135, 0.00167] | [181.54406064065452, 665.665173440235] | [0.05293670013806314, 0.20523974671561424] |
| systematic | [0.00128, 0.00174] | [142.81959167859748, 939.0429726765738] | [0.034293569392035664, 0.2493608496820379] |

finite input variations; additive envelope has no assigned coverage probability
adaptive quadrature estimates; no outward-rounding certificate
Operation counts: {'derivative_quadratures': 0, 'freeze_root_iterations': 840, 'phase_space_integrand_evaluations': 4179, 'phase_space_quadratures': 7, 'unique_weak_chains': 7}

## Generated three-quark source channels

colour factors and actual internal matter-vertex support for the retained three-quark carrier
- colour-singlet multiplicity: 1
- independent adjoint source channels: 2
- exact source Gram matrix: [['4/3', '-2/3', '-2/3'], ['-2/3', '4/3', '-2/3'], ['-2/3', '-2/3', '4/3']]
- maximum finite algebra residual: 6.66134e-16
- evaluated bound-state mass operator: False
- evaluation work: {'adjoint_constraint_matrix_actions': 24, 'binding_kernel_solves': 0, 'casimir_diagonalizations': 1, 'colour_generators': 8, 'colour_tensor_dimension': 27, 'source_vectors': 3, 'spectral_tail_evaluations': 0, 'spinor_vertex_shape': [20, 2]}

## Generated on-shell matter conditions

The generated Fermi constant and real top/Higgs pole masses specify
physical renormalization conditions of this effective realization.
The finite Yukawa, quartic and quadratic coefficients are evaluated
in the Landau-gauge tadpole-free MSbar top-Yukawa truncation.
The three gauge coefficients remain specified leading boundaries.

- Q = 91.12483998892056 GeV
- y_t = 0.9860941669637286
- lambda = 0.145267456179647
- m squared = -8585.718899938649 GeV^2
- top mass correction = 0.6726563424163345 GeV
- Higgs squared-mass correction = -2302.000479053791 GeV^2
- Born top width (m_b=0, |V_tb|=1) = 1.534454470831274 GeV
- first-order condition residuals (GeV^2): {'Higgs': 0.0, 'stationarity': -2.8421709430404007e-13, 'top': 8.526512829121202e-14}
- distinct A values: 4
- distinct B values: 7
- quadrature integrand evaluations: 84
- additional Fermi-kernel calls: 0

The source-identification interface is retained with its actual status.
These parameters and their physical conditions are recorded separately
from the production mass readouts.

## Continuous thermal evolution

same specified weak inputs; static-nucleon rates and instantaneous neutrino decoupling
- final neutron fraction = 0.1933481805061133
- final neutrino temperature = 0.000490656518982094 GeV
- EOS evaluations / requests = 75 / 205
- weak-rate evaluations / requests = 125 / 205
- quadrature calls = 975
- integrand evaluations = 266745
- cache capacity per kernel = 256

The call-local caches use exact temperature arguments and fixed physical inputs.
Operation counts come from existing quadrature diagnostics.

## Joint mass relation

The geometric mass combination uses weights 8, 9 and -17 on the three sector log ratios.
Residual: 0.
Shared log-input derivatives: [0.0, 5.551115123125783e-16, 0.0].
The physical-mass interface propagates the full joint covariance of six log masses
and their independently supplied matching coefficients.

## Joint bandwidth response

joint bandwidth sensitivity at fixed content, source and transfer coefficients

| R | c_R | v_R/v_5 | m_e,R/m_e,5 | joint relative residual |
|---:|---:|---:|---:|---:|
| 5 | 2.49353433252 | 1 | 1 | 0 |
| 6 | 2.59586403135 | 0.265502445664 | 0.129174125275 | 8.882e-16 |
| 20 | 2.66171711768 | 0.113186594651 | 0.0346085089696 | -4.441e-15 |

All R>=5 endpoint enclosure: ['2.4724098408674438', '2.7182303260682460'].
Three-position platform certified: True.
Certificate operations: {'R5_rows': 8, 'bandwidth_scan_points': 0, 'complete_rows': 26, 'distinct_gaussian_meshes': 24, 'exponential_enclosure_evaluations': 2720, 'row_subintervals': 4352, 'subintervals_per_row': 128}.
Response operations: {'analytic_boundary_terms': 182, 'frequency_quadrature_integrals': 182, 'iterative_endpoint_solves': 0, 'spectral_response_evaluations': 3}.

## Local nonlinear source feedback

self-consistent finite plane material cells before trajectory crossing
The fixed physical interval, initial masses and velocities, acceleration scale
and boundary values are registered with the calculation.

| steps | maximum energy-balance residual | mass residual | minimum cell length | field solves |
|---:|---:|---:|---:|---:|
| 20 | 3.86083981625e-11 | 0 | 0.11686044012 | 21 |
| 40 | 9.65207623028e-12 | 0 | 0.116860445311 | 41 |

Energy-error reduction factor: 4.00000966024.
Final-position difference: 2.65796231913e-07.
Time-step refinement is evaluated at fixed material-cell resolution.

## Independent-foliation effective realization

M_P^2/2 integral sqrt(-g) [R-2 Lambda-2 J(A^2)] + S_m
separate constrained reductions: flat Einstein dust/vacuum Fourier modes and accelerated static scalar velocities
Equation and evolution checks passed: True
Accelerated longitudinal threshold: 0.786151377757
Minimum kinetic coefficient in its stated normalization: -0.0814413464563
The positive dust-vacuum reduction and the negative accelerated direction belong to this action and their stated backgrounds.
The native theory is varied on its generated variables; its physical kinetic form follows from its own common constraint reduction.
The invariant-subsystem condition applies when this particular parent evolution is retained.

## Correlated BAO comparison

Fixed model: chi squared = 29.5087984551, degrees of freedom = 13, p = 0.00553993305564.
Common-scale diagnostic: alpha = 0.989282404391 +/- 0.00274031093677.
Scale contribution = 15.2966047426; orthogonal contribution = 14.2121937125.
The diagnostic projection uses the retained distances and covariance factor.

## Finite thermal-history response

range over a deterministic prediction set using the original observational covariance
- late-ionization sound horizon (Mpc): [146.86995460564577, 147.02326402733587]
- late-ionization chi-squared range: [28.049070257741462, 31.026437778316918]
- HYREC standard_atomic: sound horizon (Mpc) [146.94638604411406, 146.94638604411406]; chi squared [29.50507638285028, 29.50507638285028]
- HYREC generated_atomic: sound horizon (Mpc) [147.07454727664094, 147.07454727664094]; chi squared [27.11909550195077, 27.11909550195077]
Distance propagation work: {'additional_covariance_factorizations': 0, 'new_thermal_background_solves': 0, 'power_spectrum_solves': 0}
The late-ionization range covers its stated redshift sector. The direct atomic-input response retains the atomic and radiative-transfer approximation of its solver.

## Native scalar intensity

explicit g,Z,L realization of the native quadratic scalar intensity
Inputs: {'L': '2.5', 'Z': '2', 'g': '1', 'iterations': 55, 'shells': 128}
Pole mass squared: ['2.23644724241094130000000000000000', '2.24738228666098570000000000000000']
Positive pole residue: ['0.03632403038501140000000000000000', '0.03640371899496640000000000000000']
Continuum threshold squared: ['8.94578896964376520000000000000000', '8.98952914664394280000000000000000']
Subtracted complete response: ['0.01547620842349678589210154488835', '0.01558313904030011447119101721083']
Omitted continuum upper bound: 0.00000039529395224009424686211464
The scalar root certificate is evaluated once and reused.
Independent two-particle dispersion integrals test the rational bubble bounds.
The spectrum belongs to the declared quadratic scalar realization.

## Joint native amplitude and radius equilibrium

joint static minimum of the native unweighted relative potential at fixed g
the same relative F_L at every radius, with fixed g and Lc^2=pi

- selected radius: ['2.50662827463100050241576528481104', '2.50662827463100050241576528481105']
- scaled amplitude: ['0.11351620981990260000000000000000', '0.11376524644913700000000000000000']
- joint Hessian diagonal: [['1.57271392755068918879610012661821', '1.58387089924139139884467994503419'], ['1.81625935711844160000000000000000', '1.82024394318619200000000000000000']]
- relaxed compression curvature: ['0.18402554786471196184396578882505', '0.18442927084142120065557411167028']
- distinct additional stationary certificates: 1
- spectral tail reused: True

The same relative potential has a unique positive joint static minimum.
The source action supplies its physical density normalization and temporal terms.

## Occupied common source and metric background

one occupied classical Einstein--matter background with an algebraic native radius source

U_eta+3T-V=0, solved at each background evaluation
- dimensionless duration: 0.7236012545582676
- minimum sampled velocity curvature: 0.10024820421090548
- minimum sampled characteristic speed squared: 0.38313669332221595
- maximum relative Friedmann residual: 2.8587615403690456e-12
- maximum relative phase-charge residual: 6.352417254765309e-13
- independent phase reconstruction residual: -2.6506574712925612e-14
- operation counts: {'algebraic_source_solves': 101, 'background_rhs_evaluations': 62, 'full_potential_integrals': 18, 'generalized_characteristic_eigensolves': 17, 'initial_amplitude_restoring_evaluations': 10, 'ordinary_kinetic_eigensolves': 17, 'phase_quadrature_evaluations': 21, 'potential_restoring_function_evaluations': 378, 'reused_vacuum_root_certificates': 1, 'source_derivative_evaluations': 1280}

Continuous interval certification uses a phase-space box and an exit-time bound.
- certified dimensionless duration: ['0.010000000000000000', '0.010000000000000000']
- constrained curvature enclosure: ['0.047698002232000933', '0.154046763075088878']
- characteristic speed squared lower bound: 0.191808804731042452
- phase-clock rate enclosure: ['0.235787227561451353', '0.344307754866217144']
- certification work: {'distinct_spectral_endpoint_evaluations': 8, 'finite_max_shell': 64, 'interval_ode_steps': 0, 'potential_quadratures': 0, 'spectral_shell_pair_evaluations': 520}

This interval is certified independently of the longer floating-point trajectory.

## Nonuniform common source and metric evolution

finite-amplitude planar Einstein--scalar--auxiliary-radius evolution
Inputs: {'amplitude': 0.001, 'background_inputs': {'Z': 2.0, 'absolute_tolerance': 2e-12, 'duration': 0.7236012545582676, 'g': 1.0, 'initial_radius_squared': 9.42477796076938, 'mass_squared': 0.1193662073189215, 'planck_ratio': 1.40682609662801, 'reference_radius_squared': 6.283185307179586, 'relative_tolerance': 2e-10, 'samples': 17, 'vacuum_density': 2.8100830157697488e-120}, 'duration': 0.01, 'period': 6.283185307179586, 'points': 17, 'steps': 8}
Verification: {'algebraic_source': True, 'constraint_compatible_initial_data': True, 'einstein_hamiltonian': True, 'einstein_momentum': True, 'global_phase_charge': True, 'positive_principal_forms': True, 'real_characteristics': True, 'spatial_refinement': True, 'time_refinement': True, 'timelike_future_phase': True}
Operation counts: {'algebraic_source_solves': 6883, 'initial_constraint_evaluations': 88, 'potential_integrals': 6883, 'potential_integrand_evaluations': 144543, 'principal_eigensolves': 3009, 'rhs_evaluations': 160, 'source_response_evaluations': 61792, 'spatial_transforms': 4206}

## Expanding nonlinear response window

autonomous finite displacement window of the existing nonrelativistic RMS source action and homogeneous Einstein lapse action, with the complete periodic field solved exactly
Inputs: {'acceleration_ratio': 0.18377629847393065, 'duration': 0.05, 'initial_displacement': 0.001, 'omega_m': 0.31495570348598423, 'omega_vacuum': 0.6850442965140158, 'samples': 17, 'wavenumber': 100.0}
Common constraint: -p_a^2/(12a)+k^2 p_D^2/(M a^2)+rho_vac a^3+M+W(a,D)=0
Homogeneous limit: D=p_D=0 gives 3H^2=rho_vac+M/a^3
Local response: at fixed a the exact periodic field solves the full RMS Poisson equation for the noncrossing cold displacement
Verification: {'background_continuity': True, 'exact_flux_reconstruction': True, 'full_poisson_equation': True, 'lapse_constraint': True, 'noncrossing_flow': True, 'numerical_refinement': True, 'positive_physical_hamiltonian_hessian': True, 'retained_force_projection': True, 'uniform_exit_certificate': True}
State refinement difference: 1.0952610346448566e-14
Operation counts: {'diagnostic_phase_points': 139264, 'exact_field_reconstructions': 134, 'potential_quadratures': 134, 'quadrature_node_evaluations': 12864, 'rational_exit_certificate_evaluations': 1, 'rhs_evaluations': 98}

The retained variational equations and the omitted spatial-mode residuals are recorded separately.
