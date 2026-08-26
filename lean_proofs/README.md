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

# Lean 4 Proof Archive

This directory contains the 18 current Lean 4 proof guards of the V4
framework. They use the Lean 4 core library and compile with Lean 4.7.0.

Run one file with:

```text
lean.exe lean_proofs/<file>.lean
```

Run the complete archive through the repository verifier described in
`REVIEWER_START_HERE.md`.

## What Is Formalised

The Lean files verify finite algebraic implications from explicitly declared
premises. They cover integer counts, representation-content identities,
normalisation coefficients, beta-function coefficients, and the logical
packaging of endpoint closures. Analytic spectral results and physical
closure premises are supplied by the derivations in the companion papers;
Lean checks the finite deductions made from them.

## Numerical And Content Identities

| File | Verified content |
|---|---|
| `bbn_nonperturbative.lean` | Current BBN content relations: `g_A=4/pi`, electromagnetic shift, radiative factor, CKM factor, and phase-space dependencies. |
| `conservation_spectral_origin.lean` | Factorisation `tau^2 pi/2=(2 tau^2)(2 pi)xi` with `xi=1/N_g`. |
| `conformal_gauge_duality.lean` | Conformal-coupling arithmetic, `N_g xi=1`, and the `7/4` Weyl-content ratio. |
| `fermion_content.lean` | Left/right Weyl counts, colour vectoriality, and the five one-generation representation classes. |
| `hypercharge_derivation.lean` | Hypercharges obtained from the declared Yukawa and anomaly-cancellation equations. |
| `inverse_coupling_symmetry.lean` | Inverse-coupling closure and its content ratios. |
| `twoloop_gauge_matrix.lean` | The nine coefficients of the two-loop gauge matrix. |
| `twoloop_yukawa_quartic.lean` | Top-Yukawa and Higgs-quartic coefficient identities, including electron cascade content `20=4*5`. |
| `yukawa_gauge_mixing.lean` | The two-loop Yukawa-gauge mixing coefficients. |

## Structural Foundation

| File | Verified content |
|---|---|
| `categorical_solution.lean` | Logical relations among the declared coarse-graining and Wightman predicates. |
| `emergence_chain.lean` | Finite counting skeleton of the emergence chain and the rank-two Cartan lemma. |
| `repcat_category.lean` | The stated representation-category and Schur skeleton. |
| `su2_classification.lean` | Minimal non-trivial `SU(2)` representation dimension. |
| `th_category.lean` | Category and pullback identities used in the structural formulation. |
| `wightman_frame.lean` | Logical packaging of the declared Wightman predicates and screening relations. |

## Endpoint Cosmology

| File | Verified content |
|---|---|
| `ir_cubic_closure.lean` | In three spatial dimensions, the declared local first-gradient scale-invariant class has exponent `p=3`; the corresponding point-source exponents give the BTFR quarter power. |
| `ir_action_selection.lean` | Within the normalised spectral-quadratic `[1/1]` response class, the declared infrared and Newtonian normalisations fix the coefficient ratio `1:1:1`. |
| `endpoint_residual_cosmology.lean` | Given the endpoint, conservation, momentum-constraint, and local-residual premises, the linear cosmology, acceleration branch, and decomposition packages follow. |

The endpoint files formalise coefficient algebra and dependency logic. The
continuum derivations that supply their premises are recorded in the
cosmology section of Paper II and in the current V4 ledger.
