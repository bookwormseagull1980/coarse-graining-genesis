"""Attach the native colour source to the actual complete lepton carrier.

The colour-singlet space is recovered from the matter Casimir, including
the neutral state. Weak and Higgs operators preserve this complete space.
This exact direct-coupling calculation leaves singlet-mediated feedback
to its mixed Higgs/weak vertices, rather than assigning it a coefficient.
"""
from __future__ import annotations

import numpy as np

from cg_core.finite_connector import elementary_connector, matter_generators


def native_lepton_attachment():
    generators = matter_generators()
    colours = [value for name, value in generators.items() if name.startswith("colour_")]
    casimir = -sum(value@value for value in colours)
    eigenvalues, vectors = np.linalg.eigh(casimir)
    singlet = vectors[:, abs(eigenvalues) < 1e-12]
    if singlet.shape != (16, 4):
        raise RuntimeError("the full generated colour-singlet lepton carrier must have rank four")
    projector = singlet@singlet.conj().T
    complement = np.eye(16)-projector
    weak = [value for name, value in generators.items() if name.startswith("weak_")]
    norms = lambda values: max(float(np.linalg.norm(value, ord=2)) for value in values)
    higgs = [elementary_connector(direction)["operator"]
             for direction in ([1., 0.], [1j, 0.], [0., 1.], [0., 1j])]
    direct = norms(value@projector for value in colours)
    weak_leakage = norms(complement@value@projector for value in weak)
    higgs_leakage = norms(complement@value@projector for value in higgs)
    chirality = np.diag([1.]*8+[-1.]*8)
    left = (np.eye(16)+chirality)/2
    right = np.eye(16)-left
    left_rank = round(float(np.trace(left@projector).real))
    right_rank = round(float(np.trace(right@projector).real))
    return {
        "full_matter_dimension": 16, "complete_lepton_dimension": 4,
        "left_lepton_dimension": left_rank, "right_lepton_dimension": right_rank,
        "direct_colour_vertex_norm": direct,
        "weak_leakage_outside_complete_lepton_carrier": weak_leakage,
        "higgs_leakage_outside_complete_lepton_carrier": higgs_leakage,
        "higgs_colour_commutator_norm": norms(c@h-h@c for c in colours for h in higgs),
        "retained_weak_vertex_norm": norms(singlet.conj().T@value@singlet for value in weak),
        "retained_higgs_vertex_norm": norms(singlet.conj().T@value@singlet for value in higgs),
        "direct_colour_left_and_right_self_energy_zero": direct < 1e-13,
        "neutral_lepton_retained": True,
        "indirect_higgs_weak_feedback_evaluated": False,
        "scope": "full-carrier direct source attachment, without a family or neutral-state truncation",
    }
