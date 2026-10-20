# V5 structural closure

Status: release<br>
Version: 5.0.2<br>
V5 run: `20261020T002918Z-eff10097`

V5 is a self-contained numerical/effective framework. It does not import or
require the separate Lean physical branch. Its structural chain is recorded by
executable certificates in `cg_core/structure/` and by V5's own finite Lean
archive in `lean_proofs/`.

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**

## Chain

```text
minimal unbiased compositional change
  -> unit-covariance Gaussian width b = 1
  -> endpoints uv = sqrt(2), ir = sqrt(2*pi), critical ratio sqrt(pi)
  -> reflecting/Neumann spectrum n^2
  -> quaternion centre quotient SU(2)/{+-1} = SO(3) = RP3
  -> internal S^3 / RP^3 spectra (scalar, vector, spinor, TT)
  -> primitive trace-free charge lattice -> content sectors
  -> N_L = 8, N_R = 7, N_f = 15, sum Y^2 = 10/3, tau = 1/50
  -> endpoint kL, 4/27 TT maximum, derived R = 5
  -> common-origin gauge/flow normalization
  -> fixed spectral projection and gauge matching condition
  -> generated Yang-Mills positive spectral bottom (solved generated gap)
  -> numerical chain (masses, couplings, cosmology)
```

## Certificates

| Module | Content | Main exact/structural checks |
|---|---|---|
| `cg_core/structure/minimal_change.py` | carrier, Gaussian width, endpoints, reflection spectrum | squared endpoint identities; width one; critical ratio^2 = pi |
| `cg_core/structure/rp3_derivation.py` | quaternion centre quotient and parity towers | SU(2)/Z2 = SO(3) = RP3; scalar even, one-form odd, spinor/TT towers |
| `cg_core/structure/internal_geometry.py` | scalar/vector/spinor/TT spectra | RP3 derivation pass; formula matches `rp3_spectrum` on finite ranges |
| `cg_core/content_derivation.py` | primitive charge lattice -> six sectors | `(1,-3)`, `(3,1)`, exact hypercharges, 16-coordinate carrier |
| `cg_core/structure/content_capacity.py` | content capacity and anomalies | derived content; exact `Fraction` counts/anomaly zeros; `tau=1/50` |
| `cg_core/structure/response_level.py` | finite response level | three-position crossings and shell support select R=5 |
| `cg_core/structure/normalization.py` | gauge/flow normalization | g7/g4 zero-mode identity; unit-speed flow |
| `cg_core/structure/projection.py` | fixed response projection | fixed boundary derivative zero; moving derivative nonzero |
| `cg_core/structure/matching.py` | gauge matching condition | effective-action coefficient continuity |
| `cg_core/endpoint_interval.py` | TT endpoint root existence + uniqueness | one-time outward rational interval sum; sign-changing bracket; negative interval derivative |
| `cg_core/tt_branch_reduction.py` | full V5 TT spectrum = Lean eight-branch coefficient | exact `u=c*omega` reduction; stable active table; interval identity |
| `cg_core/structure/capacity_closure.py` | `4/27`, R=5, YM gap, collective gravity | exact factorization; endpoint certificate; interval-positive gap; two helicities |

The endpoint interval certificate is intentionally **one-time** and cached in
`certificates/endpoint_interval.json`.  Normal V5 runs load it and do not
recompute the interval spectral sum. Regenerate the ordinary structural
certificates with:

```powershell
py scripts/structure_certificates.py
```

Output: `certificates/structure_certificates.json`.

The strict endpoint existence-and-uniqueness certificate is generated only
when the spectral/interval implementation changes:

```powershell
py scripts/certify_endpoint_interval.py --cells 2048
```

Output: `certificates/endpoint_interval.json`.

The full reproduction chain also runs `scripts/structure_certificates.py` after
the numerical modules.

## Scope

The structural certificates are executable derivations and finite checks.
They do not replace a proof assistant for:

- self-adjointness and closed extensions;
- full weighted domains;
- GNS/cyclic completion;
- operator spectral theorems.

Those remain in the separate Lean physical branch and are not V5 runtime or
verification dependencies.

The exact TT reduction `A_V5(c)=A_5/c` is checked on the current bracket
`[817081/327680, 3268327/1310720]` with coefficient interval
`[0.3694084671969687, 0.3694160576081247]`.  The external Lean branch supplies
the structural operator proof; the V5 certificate supplies the numerical
branch table and the interval identity.  Neither is a runtime import of the
other.

The generated Yang--Mills gap is solved at both ends of the generated
finite-operator family: Lean at the IR edge, V5 at the TT endpoint.  No
traditional 4D QCD quantum field is constructed separately; the conventional
4D QFT route cannot construct the 4D quantum field or prove the mass gap.
