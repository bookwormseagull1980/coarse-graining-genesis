<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171

DOI records:
  [Software] 10.5281/zenodo.22067006
  [Paper I]  10.5281/zenodo.22067118
  [Paper II] 10.5281/zenodo.22067469

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
       DOI: 10.5281/zenodo.22067118
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
       DOI: 10.5281/zenodo.22067469
-->

# Endpoint-Residual Cosmology in V4

This note is the single repository-level summary of the promoted V4
cosmology branch.  It records only the current closure path.

## 1. Endpoint Split

The V4 IR endpoint is treated as a maximum-entropy endpoint of the
spectral scale flow, not as a hard pointwise cutoff.  It has two
physical projections:

```text
normal Hamiltonian projection:
  rho_Sigma
  -> cosmological cold source

local acceleration projection:
  Sigma_IR = a0^2
  -> late low-acceleration response
```

The flatness residue is therefore interpreted as

```text
Omega_Sigma = 1 - Omega_Lambda - Omega_b.
```

`Omega_DM` is retained only as a legacy table key.  The cosmological
interpretation is `Omega_Sigma`, the conserved Hamiltonian residual of
the MaxEnt endpoint.  No dark particle species is introduced.

## 2. Linear Cosmology

In homogeneous and linear cosmology the local acceleration projection
does not add a free response function:

```text
mu_eff(a,k) = 1,
Omega_cdm := Omega_Sigma.
```

The endpoint residual is propagated as a cold source:

```text
T^Sigma_mn = rho_Sigma u_m u_n,
nabla_m(rho_Sigma u^m) = 0,
p_Sigma = 0,
c_s,Sigma^2 = 0,
pi_Sigma = 0.
```

The closed linear input set is:

```text
H0 = 67.4528404666 km/s/Mpc,
Omega_b = 0.04925306386569133,
Omega_Sigma = 0.2657026396202929,
Omega_Lambda = 0.6850442965140158,
A_s = 2.101110797943e-09,
n_s = 0.965,
r = 0.025330295911,
Y_p = 0.2514,
N_eff = 3.0439,
sum m_nu = 0.06147853315 eV.
```

## 3. Photon Zero-Mode Correction

The raw photon floor gives

```text
T_CMB(raw) = 2.731008 K.
```

The promoted endpoint branch includes the finite photon zero-mode factor

```text
C_gamma = 1 - tau/pi^2,
tau = 1/50.
```

Thus

```text
T_CMB = T_CMB(raw) C_gamma
      = 2.725473978 K.
```

The accompanying `C_gamma^-3` factor is photon-number bookkeeping only.
The internal `Omega_b` closure uses the raw photon floor together with
the raw Sakharov `eta_B`; no corrected-monopole or observed-ratio value
is fed back into that computation.  If the same photon density is
rewritten in terms of the corrected monopole, the bookkeeping factor
keeps the product `eta_B n_gamma` unchanged at leading order.

## 4. CAMB Fixed-Input Propagation

With `Omega_cdm := Omega_Sigma` and the corrected photon monopole, CAMB
2.0.3 propagates the fixed V4 output set to the standard compressed
linear-cosmology observables:

```text
age = 13.78457 Gyr,
z_* = 1090.232,
r_* = 144.311 Mpc,
100 theta_* = 1.041595,

z_drag = 1060.107,
r_drag = 146.980 Mpc,

z_eq = 3414.882,
k_eq = 0.010421 Mpc^-1,

sigma8(0) = 0.81423,
S8 = 0.83428.
```

For CMB spectra, `tau_reio = 0.054` was used only as a standard
late-time visibility parameter.  It is not a V4 fundamental closure.
CAMB supplies no V4 parameter; it is a comparison propagation code.

## 5. Local Acceleration Branch

The endpoint acceleration scale is

```text
a0 = c H0/(2 pi) sqrt(4/3),
Sigma_IR = a0^2.
```

In the closed branch `a0` is the endpoint value and is not replaced by
the instantaneous FRW rate `H(z)`.

The local response is fixed as

```text
y = |grad Phi|/a0,
mu(y) = y/sqrt(1+y^2).
```

The quasi-static equation is

```text
div[mu(|grad Phi|/a0) grad Phi]
  = 4 pi G (rho_b + rho_Sigma^free).
```

In the isolated relaxed deep-IR limit with negligible free residual
density,

```text
a = sqrt(G M_b a0)/r,
v^4 = G M_b a0.
```

## 6. No-Double-Counting Rule

The observed effective dark source is

```text
rho_dark,eff = rho_Sigma^free + rho_pol,

rho_pol =
  (1/4 pi G) div[(1 - mu) grad Phi].
```

This separates the regimes:

```text
linear cosmology:
  rho_pol = 0,
  rho_Sigma is the cold source.

isolated low-acceleration galaxies:
  rho_pol can dominate the apparent dark effect.

clusters and mergers:
  rho_Sigma^free can separate from baryonic gas and source lensing
  offsets.
```

## 7. Comparison Status

The optional script

```text
scripts/validate_endpoint_cosmology.py
```

downloads public DESI DR2 BAO and SPARC data and performs fixed-parameter
comparison checks.  These observed data are not read by any prediction
module.

DESI DR2 BAO Gaussian likelihood:

```text
V4 endpoint:
  chi2 = 28.93 / 13,
  PTE = 0.00669.

Planck 2018 base-like comparison:
  chi2 = 30.16 / 13,
  PTE = 0.00447.

Planck 2018 + BAO-like comparison:
  chi2 = 18.04 / 13,
  PTE = 0.156.

DESI-only best fit with the V4 sound horizon held fixed:
  Omega_m = 0.29746,
  implied H0 = 69.08 km/s/Mpc,
  chi2 = 10.27 / 11,
  PTE = 0.506.
```

The tension is concentrated in the DESI DR2 intermediate-redshift BAO
distances.  This is a Planck-like fixed-background tension, not an
undefined-dark-sector issue.

SPARC fixed-response check:

```text
175 galaxies,
3389 points,
Y_disk = 0.5,
Y_bulge = 0.7,
mu(y)=y/sqrt(1+y^2).
```

For the curated points (`e_Vobs/Vobs < 0.1`, `Vobs > 20 km/s`):

```text
2790 points,
163 galaxies,
scatter about mean = 0.144 dex.
```

Cluster residual diagnostic:

```text
Omega_Sigma/Omega_m = 0.843619,
Omega_b/Omega_m = 0.156381.
```

A bullet-like centroid diagnostic therefore naturally places the lensing
centroid near the free endpoint residual rather than near the collisional
gas.  A full cluster likelihood still requires observed weak-lensing,
X-ray gas and cluster-light maps with covariance.

## 8. Lean Formalization

The proof guard

```text
lean_proofs/endpoint_residual_cosmology.lean
```

formalizes the logical dependency:

```text
MaxEnt endpoint
  + global sigma endpoint
  + local spatial equations
  + momentum constraints
  + visible matter conservation
  + Bianchi identity
  + no extra dark stress tensor
  + local normal residual
  -> cold endpoint residual.
```

It also formalizes the linear-cosmology package, the acceleration branch,
and the no-double-counting decomposition.  It does not formalize tensor
calculus, ADM geometry, or CAMB numerics.

## 9. Current Boundary

Closed in V4:

```text
endpoint residual interpretation,
linear CMB/P(k) source,
photon zero-mode correction,
local acceleration response,
no-double-counting rule,
fixed BAO/SPARC/cluster comparison diagnostics,
Lean logical proof guard.
```

Still external comparison work:

```text
Planck full high-l likelihood,
joint CMB/BAO/SN/RSD comparison MCMC,
multi-cluster weak-lensing map likelihood,
nonlinear rho_Sigma^free simulations,
full tensor/ADM Lean formalization.
```
