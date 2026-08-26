<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171

DOI records:
  [Software] 10.5281/zenodo.22067006
  [Paper I]  10.5281/zenodo.22067118
  [Paper II] 10.5281/zenodo.22067469
-->

# V4 Framework Ledger

This ledger describes the current formal computation. It is generated from
`cg_params.json`; numerical values below therefore match the latest fresh
reproduction. The two companion papers supply the physical derivations.

## Records

- Software: `10.5281/zenodo.22067006`
- Paper I: `10.5281/zenodo.22067118`
- Paper II: `10.5281/zenodo.22067469`

## Data Discipline

The computation has four layers:

1. `OBSERVED / anchor`: the Newton constant sets the dimensional scale.
2. Structural closure: compact RP3 spectrum, content counts, Gaussian
   heat-flow envelope, TT response, endpoint pole normalisation, and
   matching conventions.
3. `DERIVED`: values returned by the acyclic module chain.
4. `comparison`: reference observations and fixed-input propagation
   products evaluated after the internal chain.

Current store: 190 records; DERIVED=188, OBSERVED=1, SCALE_CHOICE=1.
Roles: anchor=1, cg=23, comparison=17, informational=11, internal=138.

## Defining Closures

- The one-loop TT spectral response is
  `K_TT(k^2,m^2)=k^4/(k^2+m^2)^2`; it satisfies
  `K_TT(k^2,0)=1`. The Ward-normalised subtracted flat amplitude is
  recorded separately.
- With `y=m^2/(k^2+m^2)`, the mass-weighted response is
  `y(1-y)^2`. Its unique interior maximum is `4/27` at `y=1/3`;
  the endpoint closure adopts this extremum as its pole normalisation.
- The torsion modulus is the dimensionless content invariant
  `tau=(N_L-N_R)/(N_f SumY2)=1/50`.
- The generation capacity is the declared map
  `n+3/2 < (kL)^2` on `n=0,2,4,...`; at the fixed point it returns
  `n=0,2,4`.
- The electron exponent is the content number
  `(d+1)(SumY2 Delta_f)=4*5=20`.
- The neutrino mass matrix assembles the prescribed hypercharge-trace
  eigenvalue texture and PMNS rotation. Diagonalisation verifies the
  assembled texture and its absolute Weinberg scale.

## Primary Chain

| Key | Current value | Status | Writer | Source |
|---|---:|---|---|---|
| `G_N_PDG` | `6.708830000000001e-39` | OBSERVED / anchor | `cg_core.params.init_stores` | single observed dimensional anchor |
| `M_P` | `2.435323595526305e+18` | DERIVED / internal | `scripts/init_v4.py` | reduced Planck mass from `G_N_PDG` |
| `tau` | `0.02` | DERIVED / internal | `scripts/init_v4.py` | chiral-content invariant `(8-7)/(15*(10/3))=1/50` |
| `kL` | `2.493534332522692` | DERIVED / internal | `cg_frg/frg/endpoint_constraint.py` | spin-2 endpoint fixed point |
| `M_G` | `1.731076500047502e+18` | DERIVED / internal | `cg_frg/frg/endpoint_constraint.py` | emergence scale from the endpoint fixed point |
| `lambda_long_MG` | `7.711197023651435e+36` | DERIVED / internal | `cg_frg/gravity/newton.py` | `(2,1)` long-root eigenvalue `16/L^2` at the emergence scale |
| `sigma_over_lambda_long_MG` | `1.574174556258523e-37` | DERIVED / internal | `cg_frg/gravity/newton.py` | five-channel self-energy divided by the long-root eigenvalue |
| `n_generations` | `3` | DERIVED / internal | `cg_frg/generation/window_capacity.py` | spectral-capacity map on the even RP3 Dirac tower |
| `g2_MG` | `0.5088477031823814` | DERIVED / internal | `cg_frg/gauge/geometric_couplings.py` | screened weak coupling at the emergence scale |
| `g1_MG_geo` | `0.6049900729523602` | DERIVED / internal | `cg_frg/gauge/geometric_couplings.py` | squashed-axis hypercharge normalisation |
| `g3_MG_geo` | `0.4977599162470684` | DERIVED / internal | `cg_frg/gauge/geometric_couplings.py` | colour boundary coupling |
| `v_HIGGS` | `246.1896964523894` | DERIVED / internal | `cg_frg/ewsb/vev_closure.py` | electroweak scale from the window-squared line |
| `m_e_pred` | `0.5103542513564916` | DERIVED / internal | `cg_frg/fermion/electron_mass.py` | electron cascade closure with content exponent 20 |
| `m_nu3` | `0.05017973302502751` | DERIVED / internal | `cg_frg/neutrino/neutrino_closure.py` | Weinberg scale with the squash level factor |
| `Delta_m21_sq_osc` | `7.412190153605081e-05` | DERIVED / comparison | `cg_frg/neutrino/neutrino_closure.py` | finite-window solar propagation splitting |
| `Delta_m31_sq` | `0.002511206991325586` | DERIVED / comparison | `cg_frg/neutrino/neutrino_closure.py` | atmospheric splitting of the absolute texture |
| `qcd_Lambda_QCD` | `0.2073801854594943` | DERIVED / internal | `cg_frg/qcd/qcd_sector.py` | two-loop colour running and threshold matching |

## Cosmology Closure

The entropy endpoint fixes `H0`; the neutrino floor fixes `rho_Lambda`;
their ratio gives `Omega_Lambda`. The raw photon floor, baryon asymmetry,
and proton mass give `Omega_b`, and flatness gives `Omega_Sigma`. In linear
Boltzmann propagation the residual occupies the cold-source slot. The local
endpoint projection uses `a0` and the stored `mu` response. These two
projections share the endpoint source and are evaluated in their respective
linear-cosmology and local-response branches.

| Key | Current value | Status | Writer | Source |
|---|---:|---|---|---|
| `H0_GEV` | `1.438849814296477e-42` | DERIVED / internal | `cg_frg/cosmology/gw_ratio.py` | entropy-endpoint Hubble rate |
| `Omega_Lambda` | `0.6850442965140158` | DERIVED / internal | `cg_frg/cosmology/dark_energy.py` | dark-energy content ratio |
| `Omega_b` | `0.04925306386569133` | DERIVED / internal | `cg_frg/cosmology/gw_ratio.py` | raw photon floor, raw baryon asymmetry, and proton mass |
| `Omega_Sigma` | `0.2657026396202929` | DERIVED / internal | `cg_frg/cosmology/endpoint_residual.py` | flatness endpoint residual |
| `T_CMB_corrected_K` | `2.725473977921092` | DERIVED / comparison | `cg_frg/cosmology/endpoint_residual.py` | finite endpoint correction of the photon monopole |
| `a0_MOND` | `1.204369920558342e-10` | DERIVED / internal | `cg_frg/cosmology/gw_ratio.py` | endpoint acceleration scale |
| `endpoint_acceleration_projection` | `{"a0_m_s2":1.204369920558342e-10,"a0_time_dependence":"endpoint constant","deep_ir_limit":"v^4 = G M_b a0","mu_y":"y/sqrt(1+y^2)"}` | DERIVED / informational | `cg_frg/cosmology/endpoint_residual.py` | normalised local endpoint response |
| `endpoint_sigma8` | `0.8142304448760495` | DERIVED / comparison | `cg_frg/cosmology/endpoint_residual.py` | fixed-input Boltzmann comparison propagation |
| `endpoint_S8` | `0.8342792621089947` | DERIVED / comparison | `cg_frg/cosmology/endpoint_residual.py` | fixed-input Boltzmann comparison propagation |

## Formal Verification

The archive contains 18 current Lean files. Their finite proofs
verify the implications from the premises declared in each file. Analytic
spectral and continuum premises are supplied in the papers and source
derivations. See `lean_proofs/README.md` for the exact file-level scope.

Latest verification verdict: **PASS**.

## Reproduction

From the repository root:

```text
python scripts/reproduce_v4.py
python scripts/audit_param_writers.py
python scripts/audit_observation_leakage.py
python scripts/audit_numeric_precision.py
python scripts/audit_path_portability.py
python -m pytest -q -p no:cacheprovider
python scripts/verify_lean_archive.py --lean-exe <path-to-lean.exe>
```

`scripts/verify_v4.py` combines these checks and produces
`V4_VERIFICATION_REPORT.md`. All paths recorded in reviewer-facing
artifacts are repository-relative.
