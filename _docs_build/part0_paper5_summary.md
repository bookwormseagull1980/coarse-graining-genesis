## 0.3. Paper 5 — numerical evaluation (companion series)

The framework is presented as a two-paper series:

| | Title | Role |
|---|---|---|
| Paper I | *The spectrum of a compact internal space. I. Gauge structure and fermion content* | structural foundation: gauge algebra, fermion content, gap structure |
| Paper II | *The spectrum of a compact internal space. II. Effective couplings and mass scales* | numerical evaluation: window closure, 147 parameters, observation comparison |

Paper II carries the numerical evaluation of the structural content of Paper I. Its core results:

- **Window-capacity closure**: $\kL = 2.49353$, the single dimensionless number that closes the whole chain.
- **147 parameters**: one observed anchor ($G_N$) + 146 derived quantities.
- **Accuracy**: gauge couplings $<0.01\%$, EW scale $<0.01\%$, fermion mass ratios $<1\%$, cosmological fractions $<1\%$, QCD scale $\sim1\%$.
- **Five deviations $>1\%$**, each traced to an identified source: Jarlskog $+2.95\%$ (the $|V_{ub}|$ ceiling), $m_b$ $+1.38\%$ (the $y_0=1$ anchor), $\Lambda_{\mathrm{QCD}}$ $-1.25\%$ (loop order), lightest glueball $-2.41\%$ (spectral level), $Y_p$ $+1.56\%$ (nuclear network).
- **Theoretical sensitivity** (Paper II Appendix D): elasticity matrix, convention chain, error band — the full technical detail is recorded in §0.2 above.

Paper↔code mapping:

| Paper II section | V4 code |
|---|---|
| Window capacity (sec. 3) | `cg_frg/frg/endpoint_constraint.py`, `spectral_sum.py` |
| Content & torsion $\tau=1/50$ (sec. 4) | `cg_core/ec_structure.py`, `sm_content.py` |
| Gauge couplings (sec. 5) | `cg_core/beta_functions.py`, `cg_frg/gauge/` |
| Flavour ladder (sec. 6) | `cg_frg/generation/`, `cg_frg/fermion/` |
| EW + CP (sec. 7) | `cg_frg/ewsb/` |
| Cosmology (sec. 8) | `cg_frg/cosmology/`, `cg_frg/gravity/` |
| QCD + BBN (sec. 9) | `cg_frg/qcd/` |
| Results + sensitivity (sec. 10, App. D) | `scripts/reproduce_v4.py`, `sensitivity_analysis.py`, `regime_spread.py` |

> The complete Paper II content reference (per-section core content, the 147-parameter table, the precision ledger, the theoretical sensitivity) is at the end of this document, **§11. Paper 5 (Paper II) content reference**.

---
