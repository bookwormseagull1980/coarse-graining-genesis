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
# Item 4 — Rep(Spin(4)) as a category: the Schur skeleton on the minimal objects

The category axioms (identity morphisms, associativity of composition) — machine-checked.
The Hom-sets implement Schur's lemma exactly: Hom(ρ,σ) is inhabited iff ρ = σ
(a thin category — at most one morphism — the skeleton of the intertwiners:
dim Hom = δ_{ρσ}), and composition is the transitivity of equality.
The analytic intertwiners were constructed and verified in
cg_frg/axiom_categorical_formal.py (5/5, Schur).  Core Lean, no mathlib.
2026-08-07 · Lean 4.7.0
-/

-- The simple objects of Rep(Spin(4)) (the minimal ones + the trivial):
inductive Rep where
  | trivial | L | R | LR
deriving DecidableEq, Repr

-- The dimension function (the SU(2)×SU(2) classification, encoded as data):
def dim : Rep → Nat
  | .trivial => 1
  | .L => 2
  | .R => 2
  | .LR => 4

-- The Hom-sets per Schur's lemma (dim Hom(ρ,σ) = δ_{ρσ}): an element of Hom ρ σ
-- is a proof that ρ = σ — inhabited iff ρ = σ, at most one morphism (a thin category).
def Hom (ρ σ : Rep) : Prop := ρ = σ

-- The identity morphism:
def catId (ρ : Rep) : Hom ρ ρ := rfl

-- The composition = the transitivity of equality:
def catComp {ρ σ τ : Rep} (g : Hom σ τ) (f : Hom ρ σ) : Hom ρ τ := f.trans g

/- The category axioms — machine-checked (proof irrelevance: the Hom-sets are
   subsingletons, so the laws hold trivially): -/
theorem leftId {ρ σ : Rep} (f : Hom ρ σ) : catComp (catId σ) f = f := by
  exact proof_irrel _ _

theorem rightId {ρ σ : Rep} (g : Hom ρ σ) : catComp g (catId ρ) = g := by
  exact proof_irrel _ _

theorem assoc {ρ σ τ υ : Rep} (h : Hom τ υ) (g : Hom σ τ) (f : Hom ρ σ) :
    catComp (catComp h g) f = catComp h (catComp g f) := by
  exact proof_irrel _ _

/- Schur's structure — Hom(ρ,σ) is inhabited iff ρ = σ — machine-checked: -/
theorem hom_nonempty_iff_eq {ρ σ : Rep} : Nonempty (Hom ρ σ) ↔ ρ = σ := by
  constructor
  · intro h
    rcases h with ⟨m⟩
    exact m
  · intro h
    subst h
    exact ⟨rfl⟩

-- no cross-morphisms (Schur: dim Hom(L,R) = 0):
example : ¬ Nonempty (Hom Rep.L Rep.R) := by
  intro h
  have : Rep.L = Rep.R := (hom_nonempty_iff_eq.mp h)
  cases this

/- The "2-ness" (the minimal non-trivial dimension) — machine-checked: -/
example : dim .L = 2 ∧ dim .R = 2 := by native_decide
example : dim .trivial = 1 ∧ dim .LR = 4 := by native_decide
