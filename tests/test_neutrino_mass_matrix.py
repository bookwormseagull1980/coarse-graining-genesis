# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Mass labels must agree with PMNS columns, not just sorted eigenvalues.

These tests use pure assembly functions and an in-memory compute store.
They neither require nor update cg_params.json.
"""

import math
import unittest
from unittest.mock import patch
import numpy as np
import pytest

from cg_frg.neutrino import neutrino_mass_matrix as neutrino
from cg_frg.neutrino.complex_mixing import (
    mixing_matrix, ckm_from_moduli, jarlskog, neutrino_operators, pmns_texture)
from cg_frg.neutrino.neutrino_mass_matrix import pmns_matrix


V_HIGGS = 246.18969645238943  # GeV; retained closure record
K_GUT = 4.984263355588678e16  # GeV
TAU = 0.02
S0 = 2.0 * TAU
KAPPA = math.sqrt((1.0 + S0) / (1.0 - 2.0 * S0) ** 2.5)
LEVEL_FACTOR = 1.0 + S0 * KAPPA
REFERENCE_MASSES_EV = (
    0.002607415413287687,
    0.008691384710958958,
    0.05017973302502751,
)


class NeutrinoMassMatrixTests(unittest.TestCase):
    def assert_close(self, got, want, *, rel=2e-13, abs_tol=0.0):
        self.assertTrue(
            math.isclose(got, want, rel_tol=rel, abs_tol=abs_tol),
            f"{got!r} != {want!r}",
        )

    def test_real_pmns_columns_have_the_declared_angle_convention(self):
        mixing = neutrino.pmns_matrix()
        for i in range(3):
            for j in range(3):
                product = sum(mixing[k][i] * mixing[k][j] for k in range(3))
                self.assert_close(product, float(i == j), abs_tol=5e-15)
        sin2_13 = mixing[0][2] ** 2
        cos2_13 = 1.0 - sin2_13
        self.assert_close(sin2_13, math.sqrt(3.0) / (8.0 * math.pi**2))
        self.assert_close(mixing[0][1] ** 2 / cos2_13, 3.0 / 10.0)
        self.assert_close(
            mixing[1][2] ** 2 / cos2_13, 0.5 + 2.0 / (2.0 * math.pi) ** 2
        )

    def test_each_pmns_column_carries_its_labelled_mass(self):
        for v, k_gut, level_factor in (
            (V_HIGGS, K_GUT, LEVEL_FACTOR),
            (100.0, 2.0e15, 1.0),
        ):
            result = neutrino.build_mass_matrix(v, k_gut, level_factor)
            mixing = neutrino.pmns_matrix()
            texture = result["M_flavour"]
            scale_ev = v**2 * (2.0 * math.pi) ** 2 / k_gut * level_factor * 1e9
            for column in range(3):
                with self.subTest(v=v, column=column + 1):
                    mass_ev = result[f"m{column + 1}_eV"]
                    for row in range(3):
                        # Sorting eigenvalues cannot detect exchanging columns 1 and 3.
                        lhs = scale_ev * sum(
                            texture[row][k] * mixing[k][column] for k in range(3)
                        )
                        rhs = mass_ev * mixing[row][column]
                        self.assert_close(lhs, rhs, abs_tol=2e-14 * scale_ev)

    def test_mass_values_and_dimensionless_texture_contract_are_preserved(self):
        result = neutrino.build_mass_matrix(V_HIGGS, K_GUT, LEVEL_FACTOR)
        masses = tuple(result[f"m{i}_eV"] for i in (1, 2, 3))
        for got, expected in zip(masses, REFERENCE_MASSES_EV):
            self.assert_close(got, expected)
        self.assert_close(result["r12_derived"], 0.3)
        self.assert_close(result["r23_derived"], math.sqrt(3.0) / 10.0)
        rescaled = neutrino.build_mass_matrix(2.0 * V_HIGGS, K_GUT, LEVEL_FACTOR)
        for i in range(3):
            self.assert_close(rescaled[f"m{i + 1}_eV"], 4.0 * masses[i])
            for j in range(3):
                self.assert_close(
                    rescaled["M_flavour"][i][j], result["M_flavour"][i][j]
                )
                self.assert_close(
                    result["M_flavour"][i][j], result["M_flavour"][j][i],
                    abs_tol=5e-15,
                )

    def test_compute_publishes_only_the_existing_diagnostic_keys(self):
        inputs = {"v_HIGGS": V_HIGGS, "k_GUT": K_GUT, "tau": TAU}
        inputs.update({f"m_nu{i}": m for i, m in enumerate(REFERENCE_MASSES_EV, 1)})
        published = {}

        def capture(key, value, **metadata):
            published[key] = (value, metadata)

        with patch.object(neutrino, "get", inputs.__getitem__), patch.object(
            neutrino, "pset", capture
        ):
            result = neutrino.compute()
        self.assertEqual(
            set(published), {"mnu_r12_diag", "mnu_r23_diag", "mnu_matrix_scale_check"}
        )
        self.assert_close(published["mnu_r12_diag"][0], result["r12_derived"])
        self.assert_close(published["mnu_r23_diag"][0], result["r23_derived"])
        self.assertLess(published["mnu_matrix_scale_check"][0], 2e-13)
        for _, metadata in published.values():
            self.assertEqual(metadata["provenance"], "DERIVED")


def test_ckm_exact_entries_and_quartet():
    vus, vcb, vub, delta = .2239, .040, .0037, 8*math.pi/21
    u = ckm_from_moduli(vus, vcb, vub, delta)
    np.testing.assert_allclose(u.conj().T@u, np.eye(3), atol=4e-16)
    np.testing.assert_allclose([abs(u[0,1]),abs(u[1,2]),abs(u[0,2])],
                               [vus,vcb,vub], atol=1e-16)
    c13 = math.sqrt(1-vub*vub)
    s12, s23 = vus/c13, vcb/c13
    expected = s12*s23*vub*math.sqrt(1-s12*s12)*math.sqrt(1-s23*s23)*c13**2*math.sin(delta)
    assert jarlskog(u) == pytest.approx(expected, rel=1e-13)


def test_complex_majorana_takagi_and_vacuum_operator():
    masses = np.array([.0026,.0087,.0502])
    r = neutrino_operators(masses, majorana=(.4,-.9))
    u, m, h2 = r["U"],r["M_eV"],r["H2_eV2"]
    np.testing.assert_allclose(m,m.T,atol=1e-17)
    np.testing.assert_allclose(u.T@m@u,np.diag(masses),atol=3e-17)
    np.testing.assert_allclose(h2@u,u@np.diag(masses**2),atol=2e-18)
    np.testing.assert_allclose(h2,m.conj()@m,atol=2e-18)
    assert np.linalg.eigvalsh(h2)[0] > 0
    plain = neutrino_operators(masses)
    np.testing.assert_allclose(h2,plain["H2_eV2"],atol=2e-18)
    assert np.max(np.abs(m-plain["M_eV"])) > 1e-4


def test_zero_phase_recovers_labelled_real_texture():
    np.testing.assert_allclose(pmns_texture(delta=0),pmns_matrix(),atol=2e-16)
    assert jarlskog(pmns_texture(delta=0)) == 0


def test_unphysical_inputs_rejected():
    with pytest.raises(ValueError):
        ckm_from_moduli(.9,.9,.9,1)
    with pytest.raises(ValueError):
        neutrino_operators([.1,float("nan"),.3])
    with pytest.raises(ValueError):
        mixing_matrix(.1,.2,.3,0,majorana=(1,))
