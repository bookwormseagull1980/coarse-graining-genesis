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

/-!
# Th as a formal category + the full-subcategory / pullback structure (machine-checked)

The theory category Th (objects = (content, dynamics); morphisms = theory
homomorphisms), its full subcategories MCat (content filter) and WCat (form filter),
and the pullback structure of their intersection.  The category axioms are
machine-checked (thin category: the Hom-sets are propositions).  The pullback of the
inclusions is characterized: its objects are exactly the intersection objects.
Core Lean, no mathlib.  2026-08-08
-/

-- the simple-object labels (n = 2j; the dimension is n+1; n = 0 trivial, n = 1 the
-- spin-1/2 — the infinite family; the classification is cited, su2_classification.lean):
abbrev Label := Nat

-- the dynamics datum (formal): the quantum frame (the analytic W1-W6 content is
-- literature, recorded in wightman_frame.lean) and the classical marker:
inductive Dyn where
  | quantum : Dyn
  | classical : Dyn
deriving DecidableEq, Repr

-- the theory category Th:
structure ThObj where
  content : List Label
  dyn : Dyn

-- the morphisms: a theory homomorphism = a label-preserving map of the field contents
-- (every label carried by T is carried by U); the Dyn-morphism part is trivial here:
def ThHom (T U : ThObj) : Prop := ∀ a ∈ T.content, a ∈ U.content

-- the identity morphism:
theorem catId (T : ThObj) : ThHom T T := by
  intro a ha
  exact ha

-- the composition (transitivity of the membership implication):
theorem catComp {T U V : ThObj} (g : ThHom U V) (f : ThHom T U) : ThHom T V := by
  intro a ha
  exact g a (f a ha)

-- the category axioms (proof irrelevance: the Hom-sets are subsingletons):
theorem leftId {T U : ThObj} (f : ThHom T U) : catComp (catId U) f = f := by
  exact proof_irrel _ _

theorem rightId {T U : ThObj} (g : ThHom T U) : catComp g (catId T) = g := by
  exact proof_irrel _ _

theorem assoc {T U V W : ThObj} (h : ThHom V W) (g : ThHom U V) (f : ThHom T U) :
    catComp (catComp h g) f = catComp h (catComp g f) := by
  exact proof_irrel _ _

-- the minimal non-trivial label (n = 1, i.e. j = 1/2 — the spin-1/2):
def minimalLabels : List Label := [1]

-- the content filter M (carries the minimal change — a spin-1/2 field):
def MCat (T : ThObj) : Prop := ∃ s ∈ minimalLabels, s ∈ T.content

-- the Wightman form filter: the theory is a quantum (non-classical) theory — the
-- frame condition (the analytic W1-W6 content is literature, recorded formally):
def WCat (T : ThObj) : Prop := T.dyn ≠ .classical

-- the intersection:
def WMCat (T : ThObj) : Prop := WCat T ∧ MCat T

-- the pullback structure: the pullback of the inclusions U: WCat -> Th and
-- V: MCat -> Th has, as its objects, exactly the intersection objects (for full
-- subcategories this is the object-class intersection) — machine-checked:
theorem pullback_objects_iff :
    (∃ (TW : {T : ThObj // WCat T}) (TM : {T : ThObj // MCat T}), TW.1 = TM.1)
      ↔ ∃ T : ThObj, WMCat T := by
  constructor
  · intro h
    rcases h with ⟨TW, TM, h⟩
    refine ⟨TW.1, TW.2, ?_⟩
    simpa [h.symm] using TM.2
  · intro h
    rcases h with ⟨T, w, m⟩
    exact ⟨⟨T, w⟩, ⟨T, m⟩, rfl⟩

-- the witnesses:
def T_scalar : ThObj := { content := [0], dyn := .quantum }      -- the free scalar
def T_dirac : ThObj := { content := [1, 1], dyn := .quantum }    -- the free Dirac
def T_classical : ThObj := { content := [1], dyn := .classical } -- the classical Weyl

-- the witness membership (T1 / T2 / T4):
example : WCat T_scalar ∧ ¬ MCat T_scalar := by
  constructor
  · simp [WCat, T_scalar]
  · intro h
    rcases h with ⟨s, hs, hm⟩
    simp [minimalLabels, T_scalar] at hs hm
    rw [hs] at hm
    cases hm

example : WCat T_dirac ∧ MCat T_dirac := by
  constructor
  · simp [WCat, T_dirac]
  · exact ⟨1, by simp [minimalLabels], by simp [T_dirac]⟩

example : MCat T_classical ∧ ¬ WCat T_classical := by
  constructor
  · exact ⟨1, by simp [minimalLabels], by simp [T_classical]⟩
  · intro h
    exact h rfl
