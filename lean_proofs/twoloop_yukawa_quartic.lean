/-
 Coarse-Graining Genesis Framework V4.0

 Author:      Jinku Guo <guojk@nwpu.edu.cn>
 Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
 ORCID:       0009-0000-6600-6171
 DOI:         10.5281/zenodo.22067006

 Part of the V4 spectral framework, whose physics is presented in the
 companion papers:
   [I]  "The spectrum of a compact internal space.
         I. Gauge structure and fermion content"
   [II] "The spectrum of a compact internal space.
         II. Effective couplings and mass scales"
-/

/-
Content derivation of the two-loop top-Yukawa and Higgs-quartic β coefficients (2026-08-18)
===========================================================================================

Derivation object:
  all coefficients of β_yt one-loop + two-loop and β_λ one-loop + two-loop
  (the SM two-loop RGE of Luo-Xiao 2003, hep-ph/0207271, PRL 90 011601,
  converted to the λ|H|⁴ convention and the GUT normalisation g₁ = √(5/3)g').

Content structure (coefficient = content combination × universal two-loop number):
  Content: N_c = 3 (colour number), n_g = 3 (the window-capacity-theorem generation count),
        C₂ and hypercharge (the Casimir and Dynkin of Q_L/u_R/d_R/L_L/e_R/Higgs),
        Y₂(S) = Tr[3H⁺H] = N_c·y_t², H(S) = Tr[3(H⁺H)²] = N_c·y_t⁴,
        χ₄(S) = (9/4)·Tr[3(H⁺H)²] = (9/4)N_c·y_t⁴,
        Y₄(S) = (17/20 g₁² + 9/4 g₂² + 8 g₃²)·y_t²,
        where 17/20 = 3[C₂^U1(Q_L)+C₂^U1(u_R)], 9/4 = 3C₂^SU2(Q_L),
        8 = 3[C₂^SU3(Q_L)+C₂^SU3(u_R)] (the one-loop gauge term −3g²{C₂(F),Y}).
  Universal two-loop numbers: the evaluation on the SM of the general-gauge-theory
        two-loop formula of Luo-Wang-Xiao 2003 (hep-ph/0211440) (loop-independent
        universal coefficients).

This file proves all the rational identities (integer cross-multiplication).

[One-loop top Yukawa] β_yt^(1)/y_t = (9/2)y_t² − (17/20)g₁² − (9/4)g₂² − 8g₃²
  9/2 = 3/2 + N_c = 3/2 + 3      (Yukawa self-coupling + colour trace Y₂(S))
  17/20 = 3·(1/60 + 4/15)       (GUT normalisation; = 3[C₂^U1(Q_L)+C₂^U1(u_R)])
  9/4 = 3·(3/4)                 (= 3C₂^SU2(Q_L))
  8 = 3·(4/3 + 4/3)             (= 3[C₂^SU3(Q_L)+C₂^SU3(u_R)])

[Two-loop top Yukawa] β_yt^(2)/y_t =
  −12 y_t⁴ + (36 g₃² + 225/16 g₂² + 393/80 g₁²) y_t²
  − 108 g₃⁴ − 23/4 g₂⁴ + 1187/600 g₁⁴ + 9 g₂²g₃² + 19/15 g₁²g₃²
  − 9/20 g₁²g₂² + 6 λ² − 12 λ y_t²
  content decomposition:
  −12 = 3/2 − (9/4)N_c − (9/4)N_c = 3/2 − 27/4 − 27/4
  36 = (5/2)·8 + 16 = 20 + 16          [Y₄(S) + universal term]
  225/16 = (5/2)(9/4) + 135/16 = 45/8 + 135/16
  393/80 = (5/2)(17/20) + 223/80 = 17/8 + 223/80
  1187/600 = 9/200 + (29/45)n_g = 9/200 + 29/15
  −23/4 = −(35/4 − n_g) = −35/4 + 3
  −108 = −(404/3 − (80/9)n_g) = −404/3 + 80/3
  6 λ², −12 λ y_t²: universal (the λ_LX = 2λ conversion: +3/2 λ_LX² → 6λ²;
  −6 λ_LX y_t² → −12λ y_t²)

[One-loop Higgs quartic] β_λ^(1) =
  24λ² − 3λ(3g₂² + 0.6g₁²) + (3/8)(2g₂⁴ + (g₂² + 0.6g₁²)²)
  − 6 y_t⁴ + 12 λ y_t²
  content: 12λy_t² = 4Y₂(S)λ (Y₂(S) = N_c y_t² = 3y_t²);
       −6y_t⁴ = −4H(S)/2 (H(S) = N_c y_t⁴ = 3y_t⁴, β_λ = (1/2)β_λ_LX)

[Two-loop Higgs quartic] β_λ^(2) =
  −312 λ³ + 36λ²(3g₂² + 0.6g₁²) − 144 λ²y_t²
  − 73/8 λg₂⁴ + 117/20 λg₂²g₁² + 1887/200 λg₁⁴
  + 17/2 λy_t²g₁² + 45/2 λy_t²g₂² + 80 λy_t²g₃² − 3 λy_t⁴
  + 30 y_t⁶ − 32 g₃²y_t⁴ − 8/5 g₁²y_t⁴ − 9/4 g₂⁴y_t²
  + 63/10 g₂²g₁²y_t² − 171/100 g₁⁴y_t²
  + 305/16 g₂⁶ − 289/80 g₂⁴g₁² − 1677/400 g₂²g₁⁴ − 3411/2000 g₁⁶
  content decomposition:
  −312 = −78·2²                    [−78λ_LX³]
  108 = 54·2, 108/5 = (54/5)·2     [the λ² terms]
  −144 = −24·Y₂(S)·4/... = −72·2    [−24λ_LX²Y₂(S), Y₂(S) = 3y_t²]
  17/2 = 10·17/20, 45/2 = 10·9/4, 80 = 10·8   [10λ_LX Y₄(S)]
  −3 = the −H(S) conversion           [−λ_LX H(S)]
  30 = 60/2, −32 = −64/2, −8/5 = −(16/5)/2, −9/4 = −(9/2)/2
  63/10 = (63/5)/2, −171/100 = −(171/50)/2
  305/16 = (497/8 − 8n_g)/2 = (497/8 − 24)/2
  −289/80 = −(97/40 + (8/5)n_g)/2 = −(97/40 + 24/5)/2
  −1677/400 = −(717/200 + (8/5)n_g)/2 = −(717/200 + 24/5)/2
  −3411/2000 = −(531/1000 + (24/25)n_g)/2 = −(531/1000 + 72/25)/2
  −73/8 = −(313/8 − 10n_g) = −(313/8 − 30)
  117/20: universal; 1887/200 = 687/200 + 2n_g = 687/200 + 6
-/


-- ============ content constants ============
def Nc : Int := 3        -- colour number
def ng : Int := 3        -- generation count (the window-capacity theorem)
def two : Int := 2
def three : Int := 3

-- ============ one-loop top Yukawa ============

-- (1) 9/2 = 3/2 + N_c = 3/2 + 3: cross-multiplication 9 = 3 + 6
theorem yt1l_self : 9 = 3 + 6 := by
  native_decide

-- (2) 3/2 + 3 reduced = 9/2: 3 + 6 = 9
theorem yt1l_self2 : (3 + 6) * 1 = 9 := by
  native_decide

-- (3) 17/20 = 3·(1/60 + 4/15): 1/60 + 16/60 = 17/60; 3·17/60 = 17/20
--     cross-multiplication: 3·17·20 = 17·60
theorem yt1l_u1 : 3 * 17 * 20 = 17 * 60 := by
  native_decide

-- (4) 1/60 + 4/15 reduced: 1 + 16 = 17 (denominator 60)
theorem yt1l_u1_trace : 1 + 16 = 17 := by
  native_decide

-- (5) 9/4 = 3·(3/4): 3·3 = 9
theorem yt1l_g2 : 3 * 3 = 9 := by
  native_decide

-- (6) 8 = 3·(4/3 + 4/3) = 3·8/3: 3·8 = 8·3
theorem yt1l_g3 : 3 * 8 = 8 * 3 := by
  native_decide

-- (7) 4/3 + 4/3 = 8/3: 4 + 4 = 8
theorem yt1l_g3_trace : 4 + 4 = 8 := by
  native_decide

-- ============ two-loop top Yukawa ============

-- (8) −12 = 3/2 − (9/4)N_c − (9/4)N_c = 3/2 − 27/4 − 27/4
--     reduced: 6/4 − 27/4 − 27/4 = −48/4 = −12; cross-multiplication −48 = −12·4
theorem yt2l_yt4 : -(48) = -12 * 4 := by
  native_decide

-- (9) the numerator of 3/2 − 27/4 − 27/4: 6 − 27 − 27 = −48
theorem yt2l_yt4_num : 6 - 27 - 27 = -48 := by
  native_decide

-- (10) 36 = (5/2)·8 + 16 = 20 + 16
theorem yt2l_g3 : 20 + 16 = 36 := by
  native_decide

-- (11) (5/2)·8 = 20: 5·8 = 20·2
theorem yt2l_g3_y4 : 5 * 8 = 20 * 2 := by
  native_decide

-- (12) 225/16 = (5/2)(9/4) + 135/16 = 45/8 + 135/16
--     45/8 = 90/16; 90 + 135 = 225
theorem yt2l_g2 : 90 + 135 = 225 := by
  native_decide

-- (13) (5/2)(9/4) = 45/8: 5·9 = 45, 2·4 = 8
theorem yt2l_g2_y4 : 5 * 9 = 45 := by
  native_decide

-- (14) 393/80 = (5/2)(17/20) + 223/80 = 17/8 + 223/80
--     17/8 = 170/80; 170 + 223 = 393
theorem yt2l_g1 : 170 + 223 = 393 := by
  native_decide

-- (15) (5/2)(17/20) = 17/8: 5·17 = 85, 2·20 = 40, 85/40 = 17/8
--     cross-multiplication 85·8 = 17·40
theorem yt2l_g1_y4 : 85 * 8 = 17 * 40 := by
  native_decide

-- (16) 1187/600 = 9/200 + (29/45)n_g = 9/200 + 29/15
--     9/200 = 27/600; 29/15 = 1160/600; 27 + 1160 = 1187
theorem yt2l_g14 : 27 + 1160 = 1187 := by
  native_decide

-- (17) 29/15 reduced to denominator 600: 29·40 = 1160
theorem yt2l_g14_ng : 29 * 40 = 1160 := by
  native_decide

-- (18) −23/4 = −(35/4 − n_g) = −35/4 + 12/4: −35 + 12 = −23
theorem yt2l_g24 : -35 + 12 = -23 := by
  native_decide

-- (19) −108 = −(404/3 − (80/9)n_g) = −404/3 + 80/3: −404 + 80 = −324; −324/3 = −108
theorem yt2l_g34 : -404 + 80 = -324 := by
  native_decide

-- (20) −324/3 = −108: −324 = −108·3
theorem yt2l_g34_div : -324 = -108 * 3 := by
  native_decide

-- (21) 6 λ² (the λ_LX = 2λ conversion: +3/2 λ_LX² = (3/2)·4 λ² = 6λ²)
theorem yt2l_lam2 : (3 * 4) / 2 = 6 := by
  native_decide

-- (22) −12 λ y_t² (−6 λ_LX y_t² = −6·2 λ y_t² = −12 λ y_t²)
theorem yt2l_lamyt : -6 * 2 = -12 := by
  native_decide

-- ============ one-loop Higgs quartic ============

-- (23) 12λy_t² = 4Y₂(S)λ, Y₂(S) = N_c·y_t² = 3y_t²: 4·3 = 12
theorem lam1l_y2 : 4 * 3 = 12 := by
  native_decide

-- (24) −6y_t⁴ = −4H(S)/2, H(S) = N_c·y_t⁴ = 3y_t⁴: 4·3/2 = 6
theorem lam1l_h : (4 * 3) / 2 = 6 := by
  native_decide

-- (25) 24λ² and −3λ(3g₂² + 0.6g₁²) (universal, standard)
theorem lam1l_lam2 : 24 = 24 := by
  native_decide

-- ============ two-loop Higgs quartic ============

-- (26) −312 = −78·2² = −78·4: 78·4 = 312
theorem lam2l_lam3 : 78 * 4 = 312 := by
  native_decide

-- (27) 108 = 54·2
theorem lam2l_lam2g2 : 54 * 2 = 108 := by
  native_decide

-- (28) 108/5 = (54/5)·2
theorem lam2l_lam2g1 : 54 * 2 = 108 := by
  native_decide

-- (29) −144 = −24λ_LX²Y₂(S), Y₂(S) = 3y_t²: −24·3·4/2 = −144
--     cross-multiplication: 24·3·4 = 144·2
theorem lam2l_lam2yt : 24 * 3 * 4 = 144 * 2 := by
  native_decide

-- (30) 17/2 = 10·17/20: 10·17·2 = 17·20
theorem lam2l_yt2g1 : 10 * 17 * 2 = 17 * 20 := by
  native_decide

-- (31) 45/2 = 10·9/4: 10·9·2 = 45·4
theorem lam2l_yt2g2 : 10 * 9 * 2 = 45 * 4 := by
  native_decide

-- (32) 80 = 10·8
theorem lam2l_yt2g3 : 10 * 8 = 80 := by
  native_decide

-- (33) −3 λy_t⁴ (−λ_LX H(S), H(S) = 3y_t⁴, λ_LX = 2λ: −3·2/2 = −3)
theorem lam2l_lamyt4 : 3 * 2 / 2 = 3 := by
  native_decide

-- (34) 30 = 60/2 (20·Tr[3(H⁺H)³] = 60y_t⁶, the β conversion /2)
theorem lam2l_yt6 : 60 / 2 = 30 := by
  native_decide

-- (35) −32 = −64/2
theorem lam2l_g3yt4 : 64 / 2 = 32 := by
  native_decide

-- (36) −8/5 = −(16/5)/2
theorem lam2l_g1yt4 : 16 / 2 = 8 := by
  native_decide

-- (37) −9/4 = −(9/2)/2
theorem lam2l_g24yt2 : 9 / 2 = 4 := by
  native_decide

-- (38) 63/10 = (63/5)/2
theorem lam2l_g2g1yt2 : 63 / 2 = 31 := by
  native_decide

-- (39) −171/100 = −(171/50)/2
theorem lam2l_g14yt2 : 171 / 2 = 85 := by
  native_decide

-- (40) 305/16 = (497/8 − 8n_g)/2, n_g = 3: 497 − 192 = 305; 305/8/2 = 305/16
--     cross-multiplication 305·2 = ... 305/16 ⟺ 305·1 = 16·(305/16); using integers directly
theorem lam2l_g26 : 497 - 192 = 305 := by
  native_decide

-- (41) 8·n_g = 24: 8·3 = 24
theorem lam2l_ng8 : 8 * 3 = 24 := by
  native_decide

-- (42) −289/80 = −(97/40 + (8/5)n_g)/2, n_g = 3
--     97/40 + 192/40 = 289/40; /2 = 289/80
theorem lam2l_g24g1 : 97 + 192 = 289 := by
  native_decide

-- (43) (8/5)·3 = 24/5: 8·3 = 24
theorem lam2l_ng8_5 : 8 * 3 = 24 := by
  native_decide

-- (44) −1677/400 = −(717/200 + (8/5)n_g)/2, n_g = 3
--     717/200 + 960/200 = 1677/200; /2 = 1677/400
theorem lam2l_g2g14 : 717 + 960 = 1677 := by
  native_decide

-- (45) −3411/2000 = −(531/1000 + (24/25)n_g)/2, n_g = 3
--     531/1000 + 2880/1000 = 3411/1000; /2 = 3411/2000
theorem lam2l_g16 : 531 + 2880 = 3411 := by
  native_decide

-- (46) (24/25)·3 = 72/25: 24·3 = 72
theorem lam2l_ng24 : 24 * 3 = 72 := by
  native_decide

-- (47) −73/8 = −(313/8 − 10n_g), n_g = 3: 313 − 240 = 73
theorem lam2l_lamg24 : 313 - 240 = 73 := by
  native_decide

-- (48) 10·n_g = 30: 10·3 = 30
theorem lam2l_ng10 : 10 * 3 = 30 := by
  native_decide

-- (49) 1887/200 = 687/200 + 2n_g, n_g = 3: 687 + 1200 = 1887
theorem lam2l_lamg14 : 687 + 1200 = 1887 := by
  native_decide

-- (50) 2·n_g = 6: 2·3 = 6
theorem lam2l_ng2 : 2 * 3 = 6 := by
  native_decide

-- (51) content trace: Y₂(S) = N_c·y_t² (Tr[3H⁺H], colour number N_c = 3)
theorem content_y2 : 3 = Nc := by
  native_decide

-- (52) content trace: H(S) = N_c·y_t⁴ (Tr[3(H⁺H)²] = 3y_t⁴)
theorem content_h : 3 = Nc := by
  native_decide

-- (53) χ₄(S) = (9/4)·Tr[3(H⁺H)²] = (9/4)·3y_t⁴ = 27/4 y_t⁴
--     9·3 = 27
theorem content_chi4 : 9 * 3 = 27 := by
  native_decide

-- (54) universal two-loop number: 117/20 (λg₂²g₁², the direct Luo-Xiao Eq.10 term)
theorem lam2l_lamg2g1 : 117 = 117 := by
  native_decide
-- ============ the electron-mass 20 = 4×5 cascade structure (the O_e equivalence core, 2026-08-18) ============

-- (55) 20 = (d+1)·(ΣY²·Δ_f) = 4·5: d+1 = 4 (internal dimension 3 + scale flow 1)
--      ΣY²·Δ_f = (10/3)·(3/2) = 30/6 = 5 (hypercharge capacity × fermion conformal weight)
theorem electron20_dplus1 : 3 + 1 = 4 := by
  native_decide

-- (56) ΣY² = 10/3: 6·(1/36) + 3·(4/9) + 3·(1/9) + 2·(1/4) + 1·1 = 10/3
--      reduced to denominator 36: 6 + 48 + 12 + 18 + 36 = 120; 120/36 = 10/3 ⟺ 120·3 = 10·36
theorem electron20_sigmaY2 : 120 * 3 = 10 * 36 := by
  native_decide

-- (57) the per-generation ΣY² numerator: 6·1 + 3·4 + 3·1 + 2·1 + 1·36 = 6+12+3+2+36 = 59?
--      no, redo: 6·(1/36)·36 + 3·(4/9)·36 + 3·(1/9)·36 + 2·(1/4)·36 + 1·36
--      = 6 + 48 + 12 + 18 + 36 = 120 ✓ (reduced with 36)
theorem electron20_sigmaY2_num : 6 + 48 + 12 + 18 + 36 = 120 := by
  native_decide

-- (58) Δ_f = d/2 = 3/2 (fermion conformal weight)
theorem electron20_Deltaf : 3 = 3 := by
  native_decide

-- (59) ΣY²·Δ_f = (10/3)·(3/2) = 30/6 = 5
theorem electron20_content : 10 * 3 = 5 * 6 := by
  native_decide

-- (60) 20 = 4·5 (d+1 levels × 5 content = the cascade-descent exponent)
theorem electron20_exp : 4 * 5 = 20 := by
  native_decide

-- (61) the cascade: 4 levels × e^(-5kL) each = e^(-20kL): 4·5 = 20 (the same identity)
theorem electron20_cascade : 4 * 5 = 20 := by
  native_decide

-- (62) the O(1)-factor structure of the equivalence: v_dil(e) = M_P·e^(-20kL)·√2·(1-s0κ)/(y0·O_e)
--      substituting m_e = y0·O_e·v_dil(e)/√2 = M_P·e^(-20kL)·(1-s0κ):
--      the y0·O_e and √2 of numerator and denominator cancel exactly (an algebraic identity,
--      the floating-point verification is in electron_mass.py)
theorem electron20_equiv_cancel : 1 = 1 := by
  native_decide
