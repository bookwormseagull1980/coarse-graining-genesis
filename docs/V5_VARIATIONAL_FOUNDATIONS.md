# Full-carrier response, endpoint variation and gauge-action matching

This calculation separates three questions about the V5 base chain. All
content operators act on the generated sixteen-dimensional carrier. The
production values are retained while their operator definitions and action
derivatives are evaluated explicitly.

## 1. The sixteen-dimensional response and the torsion equation

Let `chi` be the center operator and `Y` the hypercharge operator on the
complete generation, including `nu_R`. Their exact traces are

\[
 \dim H=16,\quad \operatorname{Tr}\chi=0,\quad
 \operatorname{Tr}Y=0,\quad \operatorname{Tr}Y^2=10/3.
\]

The nonzero spectrum of `Y^2` is `{1/36,1/9,1/4,4/9,1}`. Its support
projection is the polynomial

\[
 P=I-\prod_{r\in\operatorname{spec}(Y^2)\setminus\{0\}}(I-Y^2/r).
\]

This is the unique orthogonal projection onto the range of `Y`; it transforms
covariantly with `Y` under a change of basis. Direct evaluation gives

\[
 \operatorname{Tr}P=15,\qquad\operatorname{Tr}(P\chi)=1,\qquad
 \tau_{\rm gauge}
 =\frac{\operatorname{Tr}(P\chi)}{\operatorname{Tr}P\operatorname{Tr}Y^2}
 =\frac1{50}.
\]

Thus this gauge-conditioned response can be computed on all sixteen
coordinates. There is no arbitrary deletion of a coordinate. The neutral
line is the kernel of a specified generated operator. Conditioning the
observation and changing the state are nevertheless distinct operations:
on the maximally mixed full carrier, the unconditioned center response is
zero, and `Tr(P chi)/(16 Tr(Y^2))=3/160`. These are different observables.

### Which vertex sources contorsion?

For the Hermitian minimally coupled Dirac action, in an orthonormal frame,

\[
 \nabla_\mu\psi=\nabla^{\rm LC}_\mu\psi+
 \tfrac14K_{ab\mu}\gamma^a\gamma^b\psi,
 \qquad
 \frac{\partial\mathcal L_D}{\partial K_{ab\mu}}
 =\frac i8\bar\psi\{\gamma^\mu,\gamma^a\gamma^b\}\psi.
\]

For antisymmetric `a,b` this is a three-form Clifford product, dual to
the axial current in four dimensions. Hypercharge does not occur in this
minimal spin vertex. On the content carrier it tensors with the identity.
The explicit Euclidean matrices in `minimal_spin_connection_vertex` give
`V^2=I_4/16` for one ordered component; the neutral line has the same
nonzero spin vertex. The coefficient for independent antisymmetric
connection components includes both ordered entries. The conventions for
minimal torsion coupling are discussed in Shapiro, *Physical aspects of
the space-time torsion*, Phys. Rep. **357** (2002) 113--213,
[Sec. 2.3](https://arxiv.org/pdf/hep-th/0103093).

Neutral hypercharge therefore proves gauge decoupling, not spin decoupling.
The existing unit Higgs connector supplies a second direct check. Its
neutral-to-retained block has norm one. At spectral parameter `z=i`, the
computed Schur correction has rank one and norm one. The retained block
of the full resolvent agrees with the Schur resolvent; omitting the
correction changes that resolvent. This calculation uses the connector's
own basis, whose neutral index is 14, rather than the content-trace basis.

### Quadratic torsion invariants and the actual homogeneous derivative

For internal metric-compatible torsion, put
`T_abc=epsilon_dbc B_ad`. Under rotations `B` decomposes as

\[
 B=\frac{\operatorname{tr}B}{3}I+B_A+B_S,
 \qquad \dim(\mathbf1,\mathbf3,\mathbf5)=(1,3,5),
\]

where `B_A` is antisymmetric and `B_S` is symmetric and traceless.
These inequivalent irreducible real representations admit three
independent invariant quadratic norms. Direct contraction gives

\[
 \begin{split}
 I_1=T_{abc}T_{abc}&=2\|B\|^2,\\
 I_2=T_{bac}T_{abc}&=\|B\|^2-(\operatorname{tr}B)^2,\\
 I_3=T_{bba}T_{cca}&=2\|B_A\|^2.
 \end{split}
\]

Consequently `a I1+b I2+c I3` has irreducible coefficients
`2a-2b`, `2a+b+2c`, `2a+b`. An isotropic torsion tensor is uniquely
proportional to `epsilon`; the general same-order quadratic action is
not unique on symmetry grounds. Rotational invariance alone does not
derive the production ratios `b=4a,c=-7a/3`.

For exactly those production coefficients and `a=M_G^3/4`, the isotropic
action density is

\[
 \mathcal L_{\rm tors}=-18a\tau^2/L^2,
 \qquad
 \partial_\tau\mathcal L_{\rm total}
 =-36a\tau/L^2+\partial_\tau\mathcal L_{\rm matter}.
\]

Thus `tau=1/50` is stationary precisely when the actual matter action
has derivative `36a/(50L^2)` there. In units `M_G=L=1` the required
derivative is `9/50`, while the torsion-only stationary point is zero.
This is the remaining action-matching equation. A charge-trace identity
does not evaluate a spin-current expectation. The legacy function name
`torsion_field_equation` delegates to `torsion_content_modulus`; the
action derivative is evaluated separately in `ec_variation`.

### Eliminating the two trace-free sectors

The irreducible decomposition also gives the complete algebraic field
equation. Write `c_0=2a-2b`, `c_A=2a+b+2c`, `c_S=2a+b`. For a matter
term linear in torsion, decompose its actual first derivative in the same
three orthogonal sectors, `J=J_0+J_A+J_S`. Then

\[
 2c_i B_i+J_i=0,\qquad
 B_i=-\frac{J_i}{2c_i},\qquad
 \mathcal L_{\rm eliminated}=-\sum_i\frac{\|J_i\|^2}{4c_i}.
\]

These are stationary equations; a minimum additionally requires positive
Hessians. At the production ratios, the normalized dual-matrix Hessian
has eigenvalues `(-3,2/3,3)` with multiplicities `(1,3,5)` in units
`M_G=1`. The isotropic trace direction has negative quadratic curvature
before the matter response is included. The two transverse Hessians are
strictly positive. Their invertibility, rather than the equality `b=4a`
alone, is what permits their algebraic elimination.

The minimal Hermitian spin action determines which sectors are sourced.
With internal Pauli matrices and the metric-compatible contorsion

\[
 K_{abc}=\tfrac12(T_{abc}+T_{bca}-T_{cab}),
\]

its variation in all nine dual-torsion directions evaluates to

\[
 \frac{i}{8}\sum_{a,b,c}K_{bca}
 \{\gamma^a,\gamma^b\gamma^c\}
 =-\frac14\operatorname{tr}(B)I_2.
\]

Both ordered antisymmetric connection entries are included. Thus the
minimal internal source has `J_A=J_S=0` as an operator identity, before
taking a matter expectation. The invertible transverse Hessians give
`B_A=B_S=0` uniquely in this classical algebraic model. The spin vertex
tensors with `I_16` on the content carrier; its neutral coordinate is
retained. This calculation does not require setting a neutral spin
current to zero on the grounds that its hypercharge vanishes.

Consequently, three independent action invariants do not by themselves
force a change of the isotropic production background. They do affect
the transverse fluctuation Hessians and the response to any nonminimal
trace-free current. Varying `b,c` with `a-b` fixed leaves the isotropic
quadratic action unchanged while changing those transverse responses.
A positive transverse Hessian is not a proof that the entire action is
the unique action selected by the source.

### Transfer to the downstream V5 chain

`order_parameter.compute` now obtains its coefficients from `ec_action`,
checks all three algebraic Hessians, and publishes
`ec_torsion_sector_contract`. This record connects the sector calculation
to the actual retained formulas:

| Downstream quantity | Isotropic dependence | Derivative with respect to `tau` |
|---|---|---|
| Gauge torsion mass squared | `tau^2/(6L^2)` | `tau/(3L^2)` |
| Fermion torsion mass squared | `3tau^2/(8L^2)` | `3tau/(4L^2)` |
| Squash amplitude | `s0=2tau` | `2` |
| Internal curvature amplitude | `kappa=sqrt((1+2tau)/(1-4tau)^(5/2))` | `d log(kappa)/d tau=1/(1+2tau)+5/(1-4tau)` |
| Retained J=2 response eigenvalue | `lambda_EC=14+8tau+2tau^2` | `8+4tau` |
| Inverse weak-coupling torsion term | `-pi tau^2/2` | `-pi tau` |

The positive-metric domain is `-1/2<tau<1/4`. The mass entries are in the
same inverse-radius units as `spectrum_loop`, and the J=2 entry is
`L^2` times its eigenvalue. The inverse-coupling row is the explicit
torsion term; a total derivative also includes the common endpoint and
mass dependence. The same distinction applies to a total derivative of
the retained J=2 formula when the radius changes.

On this isotropic branch, the two unsourced transverse sectors do not
alter these formulas. Their determinant contributions or additional
kinetic terms, if included in a later action, require their own matching;
they cannot be inferred from a classical algebraic elimination. The
remaining trace equation is still
`partial_tau L_matter=36a tau/L^2`. Computing that expectation from the
common matter action is necessary to identify its stationary torsion
with the gauge-conditioned `1/50`. The existing downstream numbers use
that gauge-conditioned value. The transfer record states this identity
and reports the required current without substituting it as a new input.

## 2. The response maximum and an effective-action stationary point

The exact survival-profile identity is

\[
 \rho(y)=y(1-y)^2,\quad \rho'(y)=(1-y)(1-3y),\quad
 \frac4{27}-\rho(y)=(y-\tfrac13)^2(\tfrac43-y).
\]

It proves the unique maximum on `[0,1]` at `y=1/3`. It determines a
profile maximum, not which functional the generated geometry makes
stationary. For a Gaussian mode with fixed `q^2>0`, the relative action is

\[
 S_{\rm mode}(y)-S_{\rm mode}(0)=-\frac w2\log(1-y),\qquad
 S'_{\rm mode}(1/3)=3w/4.
\]

This derivative is nonzero for a nonzero single-mode weight. The
Gaussian determinant and the survival profile therefore have different
stationary equations. For a finite trace with a common mass,

\[
 \partial_{m^2}S_{\rm loop}
 =\frac12\sum_i\frac{w_i}{q_i^2+m^2}.
\]

Each mode has its own `y_i=m^2/(q_i^2+m^2)`; a single common variation
does not set every `y_i` to `1/3`. Signed species weights, vertices,
classical terms and moving-boundary terms must be retained when using
an actual effective action. `mass_stationarity_terms` evaluates the
fixed finite trace and its response derivative without equating them.

The four-dimensional angular and log-determinant factors do give the
independent measure identity

\[
 \frac12\int\frac{d^4q}{(2\pi)^4}f(q^2)
 =\frac1{32\pi^2}\int_0^\infty z f(z)\,dz.
\]

Here the factors are respectively `1/2`, `area(S^3)=2pi^2`, and
`r^3 dr=z dz/2`. This explains the radial one-loop factor. It does
not identify the endpoint's additional `V3/(32pi^2)` with a coefficient
of the four-dimensional gravitational kinetic action. Such an identity
requires the same normalized TT vertex and inverse-response action on
both sides. The production endpoint still solves its stated response
normalization equation; it is not relabelled as an action extremum.

## 3. Gauge zero-mode reduction and registered normalization

Start with the explicit higher-dimensional gauge action

\[
 S_7=\frac1{4g_7^2}\int_{M_4\times RP^3}F^a_{MN}F_a^{MN}\,dv_7.
\]

For the external constant zero mode `A_mu(x,y)=a_mu(x) psi_0(y)`, direct
substitution in the quadratic kinetic term gives

\[
 \frac1{g_4^2}=\frac1{g_7^2}\int_{RP^3}|\psi_0|^2\,dv_3.
\]

The round physical volume is `V=pi^2 R^3`. In the constant-connection
coordinate `psi_0=1`, this is `1/g_4^2=V/g_7^2`. With the normalized
eigenfunction `psi_0=V^(-1/2)`, the charged vertex is also multiplied
by `V^(-1/2)`. Dividing that vertex by the square root of its kinetic
coefficient gives the same physical coupling `g_7/sqrt(V)`. Merely
changing the mode's coordinate normalization cannot fix `g_7`.

With `R=c/M_G`, matching this reduction to the V5 prescription

\[
 g_{4,\rm V5}^2=8(M_G/M_P)^2c^{-3}
\]

requires the precise higher-dimensional coefficient

\[
 \boxed{g_7^2=8\pi^2/(M_P^2M_G).}
\]

The two sides are evaluated both as a volume integral and in simplified
form. This is a necessary and sufficient matching identity for this
constant gauge mode; its right-hand side is not inferred from the mode
integral itself. If the connection originates instead from an off-diagonal
metric component of an Einstein action, the reduction uses the Killing
vector Gram matrix and must start from that metric action rather than
substitute it for the gauge action above.

V5 now publishes `gauge_kinetic_scale_factor=(M_G/M_P)^2` as
`SCALE_CHOICE`, with a complete quantity definition and checked direct
parents `M_G,M_P`. Both the endpoint's bare coupling and the subsequent
screened coupling consume that record. Definitions of `g2_MG`,
`g2_MG_geo`, and `g2_MG_bare_constraint` identify their normalization
and projection. The screened coupling is computed from the actual bare
record, not from a second hard-coded formula that bypasses it.

The dimensional anchor cancels from this particular coupling when
`c M_G=M_P sqrt(pi)`, giving `g4^2=8pi/c^5`. That cancellation does
not determine the factor assigned to the kinetic action. At fixed
geometry, changing `g_7^2` changes the canonically normalized charged
vertex; it is not eliminated by a field-coordinate change.

## Reproducible calculation

`scripts/check_variational_foundations.py` evaluates the full-carrier
traces, spin vertex, Schur feedback, homogeneous action derivative,
profile geometry, loop measure and zero-mode matching without writing
the parameter stores. `tests/test_variational_foundations.py` checks
independent matrix contractions, simultaneous basis changes, numerical
action derivatives, exact rational torsion contractions, Schur/full
resolvent agreement and parameter-parent registration.

The three action-level matching tasks are consequently explicit:

| Quantity | Computed result | Remaining action identity |
|---|---|---|
| `tau` | Full-carrier gauge response `1/50`; three-sector variation; minimal spin source eliminates both trace-free classical sectors; neutral spin vertex and connector feedback nonzero | Evaluate the complete generated matter-current derivative and match it to `36a tau/L^2`; derive the selected quadratic-action coefficients |
| `4/27` | Unique survival-profile maximum; Gaussian action derivative differs | Derive the endpoint from the actual effective-action variation and normalize its TT kinetic vertex |
| Gauge factor | Constant-mode integral and exact required `g7^2`; production convention registered | Derive that higher-dimensional kinetic coefficient from the common generated action |

These identities are not replaced by numerically setting an action's
coefficients to the desired response values.
