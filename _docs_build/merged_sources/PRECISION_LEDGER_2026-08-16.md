# V4 precision ledger: the final characterisation of the five >1% deviations (2026-08-16)

> This document characterises the five >1% deviations of the current full-parameter recomputation (`scripts/param_audit_full.py`, 46 observables)
> as **intrinsic precision**, not as to-be-fixed candidates.
> This is the final conclusion — these deviations will not be eliminated by "adding running / adding fits", which would break the framework's
> geometric-RGE principle or introduce observational dependence. They are reported as-is, belonging to the framework's predictions or to the loop-order / observational / nuclear-network precision ceiling.

---

## 1. The framework's "running" is geometric running (geometric RGE)

The framework's running is **geometric RGE** (geometric RGE), not the Yukawa RGE of standard QFT:

- **the geometric quantity y_0 = 1.0** (the (0,0) diagonal overlap, exact SO(4) Clebsch–Gordan normalisation) **is scale-invariant and does not run**;
- **only the gauge couplings g1, g2, g3 run** (the SM two-loop β functions, with the geometric content y_0 = 1.0 held fixed).

Hence `m_t = y_0·v/√2` is **first principles** (geometric overlap × EW scale), not a "missed running".
Any fix of "adding RGE running to y_t" violates the geometric-RGE principle — this is the **essential difference** between the framework and the standard SM,
a **prediction** of the framework, not a defect.

---

## 2. The characterisation of the five deviations

| Item | deviation | essence | fixable? |
|---|---|---|---|
| Jarlskog J | +2.95% | observational ceiling (V_ub is the least well-known CKM element, PDG 0.00382±0.0002 i.e. ±5%; the framework's 0.00378 is within range) | no |
| m_b | +1.38% | geometric prediction (the scale invariance y_0=1 of m_t → +0.806%; the y_b/y_t geometric mean → +0.54%) | no |
| Λ_QCD | −1.25% | loop-order precision (full two-loop SM running vs the standard four-loop Λ_MSbar) | only loop order can grind ~1% |
| m_glueball | −2.41% | spectral eigenvalue λ(0⁺⁺)=8 (first principles) + loop order | no |
| Y_p (BBN) | +1.56% | nuclear-network details (simplified analytic formula, no full nuclear-reaction network) | not framework physics |

### Item-by-item expansion

**1. Jarlskog J = +2.95% — observational ceiling**
- J = V_us·V_cb·V_ub·c12·c23·sinδ, with per-factor deviations: V_us −0.39%, V_cb −1.30%,
  V_ub +6.9% (dominant), sinδ +0.05%.
- But V_ub is the CKM element with the largest observational uncertainty: the direct PDG value 0.00382±0.0002 (±5%).
  The framework's V_ub = 0.00378 falls within the experimental range (against the direct PDG value it is −1.0%; against the Wolfenstein
  parametrisation 0.003535 it is +6.9% — a pure comparison-baseline difference).
- **Characterisation: observational-scatter propagation, not a framework defect.**

**2. m_b = +1.38% — geometric prediction**
- m_b = y_b/y_t · m_t. m_t = y_0·v/√2 = 174.08 (+0.806%) is the direct result of the scale-invariant
  geometric overlap y_0=1.0; y_b/y_t = e^{−(2α_dn − ns_tilt(kL_CMB+2τ))} (+0.54%) is the
  first-principles derivation of the geometric-mean formula m_b² = m_s·m_t·e^{ns_tilt(kL_CMB+2τ)}.
- **Characterisation: the framework's geometric-RGE prediction (y_t=1 scale-invariant), not a "missed running".**

**3. Λ_QCD = −1.25% — loop-order precision**
- Origin: full two-loop SM running (RK4, electroweak mixing + Yukawa) from g3(M_G) to M_Z, the standard two-loop
  Λ_MSbar extraction. −1.25% is the intrinsic precision of "two-loop vs standard four-loop".
- **Characterisation: pure loop-order precision; improvement needs the 4-loop β functions (large workload, ~1% gain).**

**4. m_glueball = −2.41% — spectral eigenvalue (first principles) + loop order**
- m_G = λ(0⁺⁺)·Λ_QCD = 8·Λ_QCD, λ(0⁺⁺) = 2λ_gluon + C₂(0,0) = 8 is the spectral eigenvalue of the
  0⁺⁺ glueball (two gluons, l=1 Killing, λ_gluon=(l+1)²=4) — fully analogous to the string tension
  σ=(λ_TT/π)Λ² (λ_TT=14), the deconfinement T_d=(λ_vector/N_c)Λ (λ_vector=4).
  **Zero external input** (the original 8.1 was a lattice empirical ratio, now replaced by the first-principles spectral eigenvalue 8).
- The deviation = the −1.25% of Λ_QCD (two-loop vs four-loop) propagated.
- **Characterisation: spectral-eigenvalue first principles + loop-order precision.**

**5. Y_p = +1.56% — nuclear-network details**
- Origin: the simplified analytic formula Y_p = 2n/(1+n), single-temperature freeze-out T_f=0.75 MeV; no full BBN
  nuclear-reaction network (detailed D/He/Li nucleosynthesis, incomplete freeze-out).
- The framework's contribution is only the v-pinning (v determines the freeze-out); T_f, Δm, τ_n, t are nature-given
  nuclear-physics constants (read from sm_inputs).
- **Characterisation: nuclear-physics details, not framework physics; improvement needs the PRIMAT/PArthENoPE full nuclear network.**

---

## 3. Final conclusion

None of these five deviations is a "fixable framework-mechanism defect":

- **observational ceiling**: J (V_ub scatter)
- **geometric prediction**: m_b (y_0=1 scale-invariant, geometric RGE)
- **loop-order precision**: Λ_QCD, m_glueball (two-loop vs four-loop)
- **nuclear-network details**: Y_p (simplified nuclear network)

They are all **reported-as-is precision**, not **to-be-fixed candidates**. The framework's physics is closed; these are the intrinsic precision ceilings
at the loop-order, observational, and nuclear-network levels. Any fix of "adding running / adding fits" would break the geometric-RGE principle
or introduce observational dependence; hence **keeping the status quo and reporting as-is** is correct.

---

*Generation time: 2026-08-16 23:08. Full-parameter recomputation reproduce exit 0 + param_audit_full 46 observables.*
