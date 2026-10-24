# TT endpoint: exact V5-to-Lean branch reduction

Status: release<br>
Version: 5.0.2<br>
V5 run: `20261024T084548Z-d52375b5`

This note records the exact identity behind
`cg_core/tt_branch_reduction.py` and the Lean
`SourceTTGaussianCoefficient` coefficient model.

Current certificate:

```text
branch-check scale interval [817081/327680, 3268327/1310720]
active branches 8
coefficient    [0.3694084671969687, 0.3694160576081247]
status         PASS
```

## Setup

At the V5 endpoint fixed point,

```text
L = c,          cutoff = pi / c^2,          R = 5.
```

For a retained mode with eigenvalue coefficient `a` and mass coefficient `b`,

```text
lambda = a / c^2,
m^2    = b / c^2,
q^2    = omega^2 + lambda.
```

The TT kernel and Gaussian weight are

```text
K = (q^2 / (q^2 + m^2))^2,
G = exp(-q^2 / cutoff).
```

## Change of variable

Set `u = c * omega`.  Then

```text
q^2 = (u^2 + a) / c^2,
K   = ((u^2 + a) / (u^2 + a + b))^2,
G   = exp(-(u^2 + a) / pi),
domega = du / c,
omega_max = sqrt(5*pi - a) / c.
```

Therefore each retained mode contributes exactly `1/c` times a
`c`-independent integral.  The full finite V5 response has the form

```text
A_V5(c) = A_5 / c,
```

with

```text
A_5 = 1/(32*pi^3) sum_i w_i
      int_0^{sqrt(5*pi-a_i)}
      ((u^2+a_i)/(u^2+a_i+b_i))^2
      exp(-(u^2+a_i)/pi) du.
```

## Active branch table

The exact V5 spectral formulas give:

| source | a | b | weight |
|---|---:|---:|---:|
| scalar l=0 | 0 | 3/4 | 4 |
| scalar l=2 | 8 | 3/4 | 36 |
| gauge l=1, c2=3 | 4 | 3/2 + tau^2/6 | 192 |
| gauge l=1, c2=2 | 4 | 1 + tau^2/6 | 72 |
| gauge l=1, c2=0 | 4 | tau^2/6 | 24 |
| fermion n=0 | 9/4 | 3*tau^2/8 | 168 |
| fermion n=1 | 25/4 | 3*tau^2/8 | 576 |
| fermion n=2 | 49/4 | 3*tau^2/8 | 1008 |

The threshold is `a < 5*pi`.  The exact interval check
`49/4 < 5*pi < 16` proves that these eight rows are active and that the next
scalar (`a=24`), gauge (`a=16`) and fermion (`a=81/4`) rows are excluded on the
endpoint bracket.

## Identity

The table is exactly the eight-branch table in the Lean
`SourceTTGaussianCoefficient` module.  Consequently

```text
A_V5(c) = A_5 / c
```

exactly, not as a numerical approximation.  The V5 certificate checks the
exact branch table and the outward interval identity
`c*A_V5(c) = A_5`; the Lean `SourceTTEndpointInterval` theorem then applies to
the full V5 response, conditional on that coefficient interval.

## Scope

The equivalence is a V5 certificate and table identity.  It is not a Lean
import: V5 does not import the Lean repository, and the Lean coefficient
theorem does not import V5.  The Lean proof remains conditional on the
supplied coefficient interval.

This reduction is the bridge used for the generated Yang--Mills mass-gap
statement.  V5 and Lean solve the generated finite operator; no traditional
4D QCD quantum field is constructed separately.
