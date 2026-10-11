# ASCL submission summary

## Name

Coarse-Graining Genesis Framework

## Short description

The Coarse-Graining Genesis Framework is a Python research software package
for an auditable spectral source-to-observable calculation chain across
couplings, matter, gravity and cosmology. It carries one finite source record
through effective couplings, matter scales, macroscopic tensor response and
cosmological observables, while keeping generated quantities, comparison data
and approximations distinct. It provides finite spectral response calculations,
matter and gravity interfaces, fixed-input propagation, interval certificates
and independent regression checks for the published calculation records.

## Repository and release

- Repository: https://github.com/bookwormseagull1980/coarse-graining-genesis
- Release: `v5.0.1`
- Version-series DOI: https://doi.org/10.5281/zenodo.22067005
- License: MIT, with the attribution terms in `LICENSE`

## Verification

From a clean checkout, install the runtime and verification dependencies and
run the quickstart followed by the public core test suite:

```text
py examples/quickstart/run_example.py
py -m pip install -r requirements.txt
py -m pip install "pytest>=7.4" "mpmath>=1.3"
py -m pytest -q -m "not numerical and not auxiliary" -p no:cacheprovider
```

The public GitHub Actions workflow runs the same core test suite on
pushes and pull requests. The full release check is documented in
`REVIEWER_START_HERE.md` and includes fresh reproduction, source audits and
the optional Lean archive checks.

## Scope

The software reproduces the finite calculations and stored records described
in the companion manuscripts. It does not claim that a passing software test
alone establishes the analytic or physical conclusions of those manuscripts;
the mathematical scope, approximations and comparison data are documented in
`docs/V5_LEDGER.md` and `REVIEWER_START_HERE.md`.
