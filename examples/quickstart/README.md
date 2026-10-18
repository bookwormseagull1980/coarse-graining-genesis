# V5 quickstart

This example produces and verifies one small generated spectral record. It
uses the exact scalar spectrum of the internal `RP3` carrier, computes the
finite mode capacity, volume and scalar heat-kernel value, and compares the
result with `expected_output.json`.

From the repository root:

```powershell
py examples/quickstart/run_example.py
```

The example is intentionally independent of the optional numerical solvers.
It is a first-run smoke test, not a replacement for the full release
verification described in `REVIEWER_START_HERE.md`.
