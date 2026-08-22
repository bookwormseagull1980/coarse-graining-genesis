<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
-->

# Cosmology Research Sandbox

This folder contains exploratory cosmology diagnostics that are kept
outside the formal V4 reproduction chain.

## What This Sandbox Is

The sandbox is a place to test open cosmology questions before any
claim is promoted into the framework:

| file | role |
|---|---|
| `ir_cubic_closure.py` | tests the minimal cubic deep-IR closure needed for flat rotation curves |
| `a0_evolution.py` | compares frozen and H(z)-tracking branches for the V4-derived a0 scale |
| `background_diagnostics.py` | computes standard-background BAO, growth, and rough sigma8 diagnostics |
| `run_all.py` | regenerates all sandbox outputs |

## Boundary With The V4 Chain

The sandbox follows these rules:

| rule | consequence |
|---|---|
| read `cg_params.json` only | V4 parameters are treated as a frozen input snapshot |
| do not import `pset` or parameter writers | sandbox runs cannot change the parameter store |
| write only under `research_sandbox/cosmology/outputs` | generated diagnostics are clearly separated |
| mark observational constants as diagnostic | unit conversions or comparison data are not construction inputs |
| require tests before promotion | exploratory results do not become V4 claims by proximity |

## How To Run

From the repository root:

```bash
python -m research_sandbox.cosmology.run_all
```

The generated notes are written to:

```text
research_sandbox/cosmology/outputs/
```

Users without a Python environment can still inspect the committed
Markdown and JSON outputs in that folder.

## Current Scientific Status

The present sandbox supports three disciplined statements:

| item | status |
|---|---|
| V4 already supplies a present-day a0 scale | inherited from the main parameter store |
| linear TT propagation alone gives Newtonian 1/r potential | established in the IR audit note |
| flat rotation curves require additional nonlinear IR dynamics | tested here by the cubic closure candidate |

The sandbox does not yet derive a relativistic transparent-gravity
completion, full matter power spectrum, or CMB angular spectra.
