/-
Coarse-Graining Genesis Framework V5.0
Author: Jinku Guo <guojk@nwpu.edu.cn>
Northwestern Polytechnical University, Xi'an 710072, China
ORCID: 0009-0000-6600-6171
References:
DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
Full bibliography: REFERENCES.md and CITATION.cff.
-/

/-!
# The infinite SU(2) dimension family and the minimality theorem (machine-checked)

The dimension function of the simple objects of SU(2) (the classification, cited):
dim(n) = n+1 for the label n = 2j.  Machine-checked — for the INFINITE family:
the minimal non-trivial dimension is 2, attained uniquely at n = 1 (j = 1/2).
This is the formal content of "1/2 is the smallest change" (the minimality over all
n ∈ Nat, not just a finite skeleton).
Core Lean, no mathlib.
-/

-- the dimension of the simple object with label n = 2j (the classification, cited):
def su2dim (n : Nat) : Nat := n + 1

-- the trivial object (n = 0, j = 0) has dimension 1:
example : su2dim 0 = 1 := rfl

-- the minimal non-trivial object (n = 1, j = 1/2 — the spin-1/2) has dimension 2:
example : su2dim 1 = 2 := rfl

-- minimality: every non-trivial object (n ≥ 1) has dimension ≥ 2:
theorem min_dim (n : Nat) (hn : n ≥ 1) : su2dim n ≥ 2 := by
  unfold su2dim
  exact Nat.succ_le_succ hn

-- uniqueness: the only dimension-2 object is the minimal one (n = 1):
theorem dim2_unique (n : Nat) (h : su2dim n = 2) : n = 1 := by
  unfold su2dim at h
  exact Nat.succ.inj h

-- the minimal non-trivial dimension is 2, attained uniquely at n = 1
-- (the infinite statement — ∀ over Nat):
theorem minimal_dim :
    (∀ n : Nat, n ≥ 1 → su2dim n ≥ 2) ∧ (∀ n : Nat, su2dim n = 2 → n = 1) := by
  constructor
  · exact min_dim
  · exact dim2_unique
