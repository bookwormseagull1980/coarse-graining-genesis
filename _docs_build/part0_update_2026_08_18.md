## 0.1. 2026-08-18 update: two-loop y_t/λ coefficients content-derived (the last residual closed)

The two-loop top-Yukawa and Higgs-quartic β coefficients are now fully content-derived, and **several errors in the old hard-coded coefficients were fixed at the same time** (fixed on the spot, per iron rule 6):

**Finding**: the old beta_yt/beta_lam coefficients in `cg_core/beta_functions.py` disagree with the authoritative literature (Luo-Xiao 2003, PRL 90 011601, hep-ph/0207271 — the original SM two-loop RGE paper; Degrassi 2012 cross-validates the λ sector −32y_t⁴g₃² + 30y_t⁶): the one-loop U(1) coefficient 0.51 should be 17/20 (GUT normalisation, i.e. −17/12 g'²); the two-loop β_yt has 8/12 coefficient errors (36 vs 6, 393/80 vs 131/16, 1187/600 vs 1187/216, 19/15 vs 199/9 — 199 was a typo for 19, −9/20 vs +3/4 sign error, the λ term +6/−12 vs −3/2/+6); β_λ two-loop was missing ~15 terms with several sign errors.

**Fix**: all coefficients rewritten per Luo-Xiao Eq. 3/6/9/10 (λ_LX = 2λ converted to the λ|H|⁴ convention, g₁ GUT-normalised), content-derived (9/2 = 3/2 + N_c; gauge term = −3[C₂(Q_L)+C₂(u_R)]/group; Y₂(S)=N_c·y_t², H(S)=N_c·y_t⁴, χ₄(S)=(9/4)N_c·y_t⁴, the 17/20/9/4/8 of Y₄(S) = one-loop content; n_g=3 window capacity; the rest are universal two-loop numbers). beta_light_yukawa corrected in sync (Luo-Xiao Eq. 3-5 form).

**Verification**: `beta_functions.py` self-test all green (one-loop b_i + two-loop B_ij/A_i + all y_t/λ coefficient assertions); Lean `twoloop_yukawa_quartic.lean` 54 theorems exit 0; reproduce_v4 ALL MODULES PASSED (the physics-chain numbers are bit-for-bit identical to before the fix — the framework's predictions do not depend on the SM table); audit CLEAN. The SM table (sm_inputs.json) updated: g₁/g₂/g₃_MG changed <0.0001% (g2_MG 0.50884433→0.50884497, conservation-law deviation +0.00066%→+0.00054%), yt_MG 0.3735→0.3660 (−2%), lambda_MG 0.00753→0.00651 (−13.6%, two-loop λ completed). The paper's Appendix C gained §derivytlam (complete one-loop + two-loop derivation of y_t/λ), compiles clean at 47 pages.

---
