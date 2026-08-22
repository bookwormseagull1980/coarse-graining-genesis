/-
 Coarse-Graining Genesis Framework V4.0

 Author:      Jinku Guo <guojk@nwpu.edu.cn>
 Affiliation: Northwestern Polytechnical University, Xi'an 710072, China

 Part of the V4 spectral framework, whose physics is presented in the
 companion papers:
   [I]  "The spectrum of a compact internal space.
         I. Gauge structure and fermion content"
   [II] "The spectrum of a compact internal space.
         II. Effective couplings and mass scales"
-/

/-!
# Item 3 — the Wightman frame: W1-W6 as formal predicates; the filter theorems within the frame

T1 (W ⊬ M), T2 (M ∩ W non-empty), T4 (M ⊬ W) — machine-checked in the formal frame.
The ANALYTIC content (the free fields satisfy W1-W6) is the cited literature
(Streater–Wightman); the frame records it formally.  Core Lean, no mathlib.
2026-08-07 · Lean 4.7.0
-/

-- The relevant simple objects of Rep(Spin(4)):
inductive Rep where
  | trivial | L | R | LR
deriving DecidableEq, Repr

-- The minimal non-trivial simple objects (the "2-ness"):
def minimal : List Rep := [.L, .R]

-- The theory frame: field content + dynamics datum + the W1-W6 formal predicates:
structure Theory where
  content : List Rep      -- the field content (the spin content)
  dynamics : String       -- the dynamics datum (formal)
  w1 : Prop               -- Hilbert space + unitary Poincaré representation
  w2 : Prop               -- fields as operator-valued distributions on a dense domain
  w3 : Prop               -- spectral condition
  w4 : Prop               -- unique vacuum
  w5 : Prop               -- locality (with the spin-statistics connection)
  w6 : Prop               -- completeness

-- The Wightman category predicate (the "correct mathematical form"):
def W (T : Theory) : Prop := T.w1 ∧ T.w2 ∧ T.w3 ∧ T.w4 ∧ T.w5 ∧ T.w6

-- The content filter M (carries at least one minimal simple object) and the chiral filter:
def M (T : Theory) : Bool := minimal.any (fun s => T.content.contains s)
def M_chiral (T : Theory) : Bool := minimal.all (fun s => T.content.contains s)

-- The witnesses.  The satisfaction of W1-W6 for the FREE fields is the cited literature;
-- the frame records it formally (the analytic verification is not re-derived here):
def freeScalar : Theory :=
  { content := [.trivial], dynamics := "□",
    w1 := True, w2 := True, w3 := True, w4 := True, w5 := True, w6 := True }

def freeDirac : Theory :=
  { content := [.L, .R], dynamics := "γ·∂",
    w1 := True, w2 := True, w3 := True, w4 := True, w5 := True, w6 := True }

def classicalWeyl : Theory :=
  { content := [.L], dynamics := "σ·∂",
    w1 := False, w2 := False, w3 := False, w4 := False, w5 := False, w6 := False }
  -- classical (non-quantised): NOT a Wightman theory

/- T1: W does NOT imply M — the free scalar is in WCat but carries only the trivial rep. -/
theorem scalar_in_W : W freeScalar := by
  unfold W freeScalar
  repeat constructor

theorem T1 : M freeScalar = false := by native_decide

example : W freeScalar ∧ M freeScalar = false := And.intro scalar_in_W T1

/- T2: the intersection is non-empty — the free Dirac is in WCat and carries the chiral pair. -/
theorem dirac_in_W : W freeDirac := by
  unfold W freeDirac
  repeat constructor

example : W freeDirac ∧ M freeDirac = true ∧ M_chiral freeDirac = true := by
  exact ⟨dirac_in_W, by native_decide, by native_decide⟩

/- T4: M does NOT imply W — the classical Weyl carries a minimal simple object
   but is not a Wightman theory (no quantisation). -/
example : M classicalWeyl = true ∧ M_chiral classicalWeyl = false := by native_decide

example : ¬ W classicalWeyl := by
  unfold W classicalWeyl
  simp

-- Computed filter values, checked without producing verifier output:
theorem computed_filter_values :
    M freeScalar = false ∧
    M freeDirac = true ∧
    M classicalWeyl = true ∧
    M_chiral classicalWeyl = false := by
  native_decide
