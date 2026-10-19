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

### Computing the connection curvature before choosing action coefficients

The complete connection contraction now fixes a comparison which the
isotropic ansatz by itself could not determine. Use Cartan's convention
`T^a=de^a+omega^a_b wedge e^b` and write `omega=omega_LC+C`. In an
orthonormal frame,

\[
 C_{ab,c}=-\tfrac12(T_{abc}+T_{bca}-T_{cab}),\qquad
 T_{abc}=C_{ac,b}-C_{ab,c}.
\]

At an LC-normal frame the curvature difference is `d_LC C+C wedge C`.
Put `S=B^T-(tr B)I/2`; direct epsilon contraction gives
`C_ab,c=epsilon_abd S_dc`. Contracting the matrix commutator then yields

\[
 \begin{split}
 R(\omega)-R_{\rm LC}
 &=\nabla_a J_a+\operatorname{tr}(S^2)-(\operatorname{tr}S)^2\\
 &=\nabla_a J_a+\operatorname{tr}(B^2)
                    -\tfrac12(\operatorname{tr}B)^2\\
 &=\nabla_a J_a+\tfrac14 I_1+\tfrac12 I_2-I_3,\qquad
 J_a=2\sum_b C_{ab,b}=-2\sum_bT_{bb a}.
 \end{split}
\]

Here `tr(B^2)` is a matrix trace, not the squared Frobenius norm of an
arbitrary nonsymmetric `B`. These formulas hold on the entire nine-component
torsion space. The divergence is retained in `scalar_curvature_difference`,
including all covariant-derivative components. For smooth global torsion
on closed RP3 its integral vanishes by Stokes' theorem. A region with
boundary carries the displayed boundary flux. The isotropic specialization
is exactly the existing `-3 tau^2/(2L^2)` curvature correction.

The scalar-curvature coefficients are consequently `(1/4,1/2,-1)`.
The production coefficients `(1/4,1,-7/12) M_G^3` are not proportional
to them. Matching the isotropic trace fixes the only possible overall
factor to `3 M_G^3`. The complete identity is

\[
 \boxed{\quad
 \mathcal L_{\rm prod}
 =3M_G^3\bigl(R(\omega)-R_{\rm LC}-\nabla_aJ_a\bigr)
   +M_G^3\left(\tfrac{10}{3}\|B_A\|^2
                         -\tfrac32\|B_S\|^2\right).
 \quad}
\]

Thus an overall normalization can match the trace saddle but cannot
identify the full actions. Their transverse fluctuations differ. This
is an exact decomposition of the selected production functional; it
does not derive its additional two coefficients, nor the gravitational
prefactor, from rotation invariance. In particular, replacing that
functional by scalar curvature alone would change the transverse
Hessians and the resulting fluctuation determinant. The comparison is
included in the downstream torsion-sector contract.

There is also a signed convention to fix before transporting a stationary
value. The existing spin calculation uses the table `K=-C`. Its Pauli
vertex is `-(tr B)I/4`, whereas inserting `C` into the same Hermitian
spin action gives `+(tr B)I/4`. The actual connection and spin operator
agree after `B_Cartan=-B_existing`. Curvature norms do not reveal this
sign because they are quadratic. `cartan_spin_connection_vertices`
evaluates all nine components and makes the conversion explicit; the
previous stationary calculations keep their stated existing spin
orientation throughout.

For the minimally coupled Yang--Mills action there is a separate exact
identity. In the same connection,

\[
 F_{ab}=\nabla^\omega_a A_b-\nabla^\omega_b A_a
          +T^c{}_{ab}A_c+[A_a,A_b]
       =\nabla^{\rm LC}_a A_b-\nabla^{\rm LC}_b A_a+[A_a,A_b].
\]

The contorsion cancels before `F` is squared, including for noncommuting
gauge matrices. Therefore the fixed-metric minimal Yang--Mills term has
no explicit algebraic torsion current. The production gauge insertion
`tau^2/(6L^2)` is not obtained by omitting the torsion term in this
identity. Its use as a response insertion is distinct from deriving it
from a common connection action. Changes of geometry, interacting states
or nonminimal terms must be varied in their actual functionals.

### Which quadratic coefficients the minimal operators can generate

The Clifford contraction also gives an operator identity, before any
spectral expansion. For every trace-free perturbation `B_perp(x)`,

\[
 D_{B+B_\perp}=D_B,
 \qquad D_B=D_0-\tfrac14\operatorname{tr}(B)I.
\]

At fixed metric, measure and torsion-independent regulator, every
well-defined determinant or resolvent of this operator has the same
identity. Its derivatives in the eight trace-free directions vanish to
all orders. This statement allows position-dependent trace-free fields;
it follows pointwise from the vertex, rather than from a homogeneous
ansatz. The minimal gauge curvature is likewise independent of `B`, as
shown above. A scalar action formed from `d`, the metric and the LC
curvature is independent of `B` as well. Integrating these specified
Gaussian operators therefore supplies no missing transverse algebraic
torsion term.

There is a useful stronger test at quadratic, zero-derivative order.
Even if a scalar insertion proportional to the full connection scalar
curvature is included, its algebraic quadratic variation at the round
zero-torsion background has the curvature direction. Together with the
spin trace direction, the accessible coefficient space is

\[
 \operatorname{span}\{(-\tfrac12,-1,1),(1,0,0)\}
 \quad\text{in the }(\|B_0\|^2,\|B_A\|^2,\|B_S\|^2)\text{ basis}.
\]

Every element satisfies `c_A+c_S=0`. The actual production action gives

\[
 c_A+c_S=\tfrac13+\tfrac32=\tfrac{11}{6}.
\]

This exact nonzero pairing proves that no choice of the two displayed
response coefficients generates the production action. The test is
implemented by `minimal_algebraic_torsion_span`; it does not exclude
additional nonminimal source vertices, derivative terms or metric
fluctuations. Those terms need their actual operator contractions. In
particular, increasing the numerical resolution of the trace-only
fermion determinant cannot determine these transverse coefficients.

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

### The coupled classical variation and the signed Dirac square

The minimal matter current can be computed as a field functional, rather
than supplied as an unspecified source. At fixed round RP3 geometry,
on the complete matter fibre, the minimal action just derived is

\[
 S(B,\bar\psi,\psi)
 =\sum_{i=0,A,S}c_i\|B_i\|^2
  +\bar\psi\bigl(D_0-\tfrac14\operatorname{tr}(B)I\bigr)\psi.
\]

Here the row and column matter fields are independent variational
variables. The identity in the spin vertex includes the neutral matter
coordinate. The complete equations are

\[
 2\sum_i c_i B_i-\tfrac14(\bar\psi\psi)I_3=0,
 \qquad D_B\psi=0,\qquad\bar\psi D_B=0.
\]

There is no extra source in these equations. The two transverse equations
give `B_A=B_S=0` at the production coefficients. Put `B=(tau/L)I_3`.
The signed native RP3 spectrum then gives

\[
 D_\tau=D_0-\frac{3\tau}{4L}I,\qquad
 \left|\lambda(D_0)\right|\ge\frac{3}{2L}.
\]

Throughout the positive-metric interval `-1/2<tau<1/4`, the triangle
inequality yields the uniform, all-shell lower bound

\[
 \left|\lambda(D_\tau)\right|
 \ge\frac{3/2-3|\tau|/4}{L}>\frac{9}{8L}.
\]

Thus both classical matter fields vanish at a stationary point. The
remaining equation is `-36a tau/L^2=0`, so the unique stationary torsion
of this minimal classical action in that interval is `tau=0`. Reversing
the Clifford orientation reverses the linear spin vertex but leaves
this gap argument and conclusion unchanged. This is a stationary-point
statement, not a claim that the negative bare trace Hessian is stable.

In units `M_G=L=1`, the exact first derivative at the charge-response
value `tau=1/50` is `-9/50` once the classical matter equations hold.
For a general matter configuration the same equation would require

\[
 \bar\psi\psi=-\frac{48a\tau}{L};
 \qquad (\bar\psi\psi)_{\tau=1/50}=-\frac6{25}
 \quad(M_G=L=1).
\]

That bilinear cannot be substituted as an independently chosen input:
it must also satisfy the matter equations, which exclude it in this
minimal classical model. At the effective-action level it would instead
be a condensate computed from the common interacting action. A finite
charge trace does not compute such a condensate. Metric variation,
Yukawa vertices and fluctuation determinants are not part of the
displayed minimal action; their derivatives belong to the complete
effective stationarity equation.

The operator calculation also fixes its square before any averaging:

\[
 D_\tau^2=D_0^2-\frac{3\tau}{2L}D_0
               +\frac{9\tau^2}{16L^2}I.
\]

The retained production insertion `3tau^2/(8L^2)` omits the signed linear
term and has a different quadratic coefficient. Even an average of
opposite Dirac eigenvalues would give `9/16`, not `3/8`. For the first
two native shells at `L=1,tau=1/50`, the minimally coupled squares are
`2.205225` and `6.325225`; the production response values are `2.25015`
and `6.25015`. Summing sixteen content coordinates multiplies these
terms; it does not change their operator coefficients.

A change of the torsion coordinate cannot fix this difference. For
`tau_old=c tau_new`, the actual square retains a term linear in every
signed `D0` unless `c=0`; that value also removes its quadratic term.
Even in a genuinely paired two-sign spectrum, replacing the operators
by their mean before taking the determinant loses a second-order term.
Write `v=-3tau/(4L)` and let `A>0` denote the shared regulated reference
denominator. The exact identity is

\[
 (A+v^2+2dv)(A+v^2-2dv)=(A+v^2)^2-4d^2v^2.
\]

`paired_dirac_determinants` evaluates this comparison exactly. Setting
`c^2=2/3` could match the isolated coefficients `9/16` and `3/8`, but
does not remove the signed term or the determinant difference; it also
changes the coefficient of the same geometric torsion tensor. Thus
neither reparametrization nor sign averaging identifies the production
insertion with the minimal connection action. On RP3 a missing sign
partner must not be supplied merely to perform this comparison.

`minimal_coupled_action_variation` evaluates all nine torsion derivatives
and both matter derivatives of the displayed action.
`minimal_classical_stationarity` records the all-shell argument and
exact residual, and `minimal_torsion_spectral_terms` compares the signed
operator with the retained response catalogue. The programme below
therefore does not identify a charge-response value with a stationary
connection merely because both have been denoted by `tau`.

### Exact auxiliary elimination and the induced interaction

Let `rho=bar(psi)psi`, with the contraction taken on the complete matter
fibre. Only the trace coefficient `c0=2(a-b)` enters the isotropic
background. The exact square completion is

\[
 S_\tau=\frac{3c_0}{L^2}\tau^2-\frac{3}{4L}\tau\rho
 =\frac{3c_0}{L^2}\left(\tau-\frac{L\rho}{8c_0}\right)^2
   -\frac{3\rho^2}{64c_0}.
\]

For `c0!=0` the stationary auxiliary value and reduced interaction are

\[
 \tau_* =\frac{L\rho}{8c_0},\qquad
 S_{\rm induced}=-\frac{3}{64c_0}\rho^2.
\]

At the production coefficients `c0=-6a`, these become
`tau_*=-L rho/(48a)` and `S_induced=rho^2/(128a)`. In unit-M_G
normalization `a=1/4`, the latter coefficient is exactly `1/32`.
`eliminate_minimal_trace_torsion` evaluates the identity in rational
arithmetic. This is a stationary algebraic elimination. It does not
define a convergent Euclidean integral over a negative quadratic form.
Its induced interaction must not be added a second time when the same
auxiliary field is retained in a fermion determinant.

The classical vanishing-field result does not evaluate an interacting
bilinear expectation. A nonzero expectation must follow from the same
reduced interaction, or equivalently from a consistently defined
auxiliary-field effective action. No independently assigned spin current
is introduced by this reduction. The transverse coefficients still enter
transverse fluctuations if those fluctuations are integrated.

For an auxiliary/physical Hessian, differentiation after stationary
elimination gives

\[
 H_{\rm reduced}=H_{XX}-H_{X\tau}H_{\tau\tau}^{-1}H_{\tau X}.
\]

Invertibility of the auxiliary block is the elimination condition;
physical stability is checked on the reduced physical form. A negative
bare auxiliary curvature is not, by itself, a propagating instability.
`eliminate_auxiliary_hessian` retains the whole mixed block.

### One action for the regulated Gaussian spin response

`cg_frg/ewsb/torsion_response.py` computes the next variation directly
from the signed operator. For each reference eigenvalue `d_n` of `D0`,
put `lambda_n=d_n^2`, `v=3/(4L)` and

\[
 \delta_n(\tau)=(d_n-v\tau)^2-d_n^2,
 \quad A_{n,k}(\omega)=\omega^2+\lambda_n+
 R_k(\omega^2+\lambda_n),
 \quad R_k(z)=\frac{z}{e^{z/k^2}-1}.
\]

The projection `omega^2+lambda_n<R k^2` and the regulator are held
fixed during tau differentiation. This is the fixed-reference convention
already used by the V5 finite response domain; it is not a moving
projection of `D_tau`. With the existing Weyl trace weight, the relative
Gaussian fermion action density is

\[
 F_k(\tau)=-\frac1{V_3}\sum_n g_n
   \int_{-\Omega_n}^{\Omega_n}\frac{d\omega}{2\pi}
        \log\left(1+\frac{\delta_n(\tau)}{A_{n,k}(\omega)}\right),
 \qquad \Omega_n=\sqrt{Rk^2-\lambda_n}.
\]

Here `V3=pi^2 L^3`. The source projection assigns the eight left
components to odd signed shells and the eight right components to even
signed shells. Thus `g_n=8 N_gen (n+1)(n+2)`; the neutral right line
contributes `N_gen (n+1)(n+2)` on every even shell. Intrinsic Dirac sign
and four-dimensional chirality are not identified as operators; this
is the particular source projection already retained in V5.

The minimal torsion vertex is the identity on the content fibre, so the
charged--neutral off-diagonal fermion blocks vanish on this background.
Eliminating the neutral Gaussian block therefore leaves its own log
determinant in the action for tau. Its gauge charge is zero, but its
tau derivative is not: omitting that determinant would change the
stationary equation. Both contributions are included in `F_k` above.

The actual first and second variations of this one action are

\[
 J_k=-\frac1{V_3}\sum_n g_n\int\frac{d\omega}{2\pi}
            \frac{\delta'_n}{A_{n,k}+\delta_n},
\qquad
 H_k=\frac1{V_3}\sum_n g_n\int\frac{d\omega}{2\pi}
 \left[\frac{(\delta'_n)^2}{(A_{n,k}+\delta_n)^2}
             -\frac{\delta''_n}{A_{n,k}+\delta_n}\right],
\]

where `delta'_n=-2v(d_n-v tau)` and `delta''_n=2v^2`. The associated
bilinear is `rho_k=-J_k/v`; its sign and magnitude are computed.
The gauge-neutral contribution is evaluated separately and retained.
The unit-M_G EC plus Gaussian-fermion equation is consequently

\[
 G_k(\tau)=\frac{6c_0}{L^2}\tau+J_k(\tau)=0.
\]

This calculation uses the production quadratic coefficients with their
declared normalization. It does not derive those coefficients from
rotational symmetry. It also does not replace the retained catalogue
insertion `3tau^2/(8L^2)` by stealth: the operator-derived response is a
separate calculation with its own signed spectrum.

`certify_fermion_window_response` encloses the continuous frequency
integrals by outward rational rectangles on `omega=Omega_n u`,
`0<=u<=1`. The reference propagator `z/(1-exp(-z/k^2))` is increasing,
since `exp(x)>1+x` for `x>0`, so its endpoint enclosures bound every
rectangle. Exact rational pi/exponential enclosures are taken from the
existing interval kernel. No difference between two quadrature grids is
used as a rigorous error estimate. Bounds on `G'_k` over an entire
supplied tau interval, together with opposite endpoint signs, establish
existence and uniqueness there. The finite measurement domain is part
of this calculation, not a claim that the full Gaussian tail is zero.

`solve_torsion_response.py` holds the stored TT endpoint `kL` fixed and
uses `k=1` in emergence-scale units. The stored radius is interpreted as
its decimal point value; the torsion enclosure does not certify the
separate endpoint computation. The result is stationarity of the EC
plus Gaussian fermion block. Gauge/Higgs interactions, metric variation
and their coupled Schur response are not supplied by holding that
radius fixed. No generated parameter-store value is overwritten.

The Landau quartic in `order_parameter.lambda_quartic` is reconstructed
from the already retained `phi0=2tau`. Its stationary equation therefore
cannot independently determine tau. The Gaussian response above does
not consume that quartic or insert a target-dependent linear term.

For the stored point value `L=2.4935343325226915`, `k=1`, `R=5` and
three generations, 512 rational integration cells give

\[
 -0.0306684016535989\leq\tau_*\leq-0.0297723339558305,
 \qquad \tau_*\simeq-0.030220367804714675.
\]

On the whole search interval `[-0.49,0.24]`, the common-action Hessian
lies in `[-1.4875255821690794,-1.2167909737515575]`. The first
derivative is positive at the left endpoint and negative at the right
endpoint, proving that this saddle exists and is unique on that
interval. At the retained gauge-response coordinate it instead obeys

\[
 -0.0695058669678698\leq G_k(1/50)
                \leq-0.0684174949746179<0.
\]

Thus the fixed-geometry EC--Gaussian-fermion block does not reproduce
`1/50` as its stationary torsion. At the numerical saddle the neutral
right current is approximately `0.06028594585864595`, and is not
decoupled. These are results for the displayed action and fixed
reference domain. They neither equate the gauge content response to a
connection saddle nor replace the downstream response coordinate.

### The same saddle solves all nine homogeneous algebraic torsion equations

The determinant need not be restricted to an isotropic trial field. The
minimal vertex already evaluated on all nine directions gives
`D_B=D0-tr(B)/4`. Hence at fixed geometry and reference window its
relative action is exactly `F_k(L tr(B)/3)` for any constant dual matrix `B`.
The complete action, gradient and Hessian are therefore

\[
 \begin{split}
 S(B)&=\sum_{i=0,A,S}c_i\|B_i\|^2+F_k(L\operatorname{tr}B/3),\\
 \nabla_B S&=2\sum_i c_i B_i+\tfrac L3F'_k I,\\
 H_B&=\left(2c_0+\tfrac{L^2}{3}F''_k\right)P_0
                     +2c_AP_A+2c_SP_S.
 \end{split}
\]

The projections are orthogonal for the Frobenius pairing. The production
transverse coefficients are nonzero, so the two transverse equations
force `B_A=B_S=0`; this is now a consequence of the full determinant
variation. The trace equation is precisely `G_k(tau)=0`. Consequently
the certified scalar root is the unique stationary point among all nine
torsion components whose trace coordinate lies in the certified interval,
with no bound imposed on the transverse matrices. The trace eigenvalue
is `L^2 G'_k/3`, and the transverse eigenvalues are `2/3` and `3`, of
multiplicities three and five. For the reported certified interval the
full homogeneous auxiliary Hessian has eight positive and one negative directions,
with no zero mode. Its negative direction remains an auxiliary saddle;
physical stability requires the reduced interacting Hessian.

At the stored geometry the certified trace eigenvalue lies in
`[-3.0830026151526404,-2.5218858748634153]` throughout the search domain.
At the numerical root its value is approximately `-2.8459534741741273`;
the largest of the nine gradient residuals is `4.2e-17`. The residual
is a numerical check; existence and uniqueness use the interval bounds
and the nonzero transverse coefficients above.

`torsion_matrix_window_action` computes this complete matrix variation.
`solve_torsion_window` carries its all-component uniqueness and Hessian
bounds into the same certificate, without a second numerical root fit.
Independent differences of the tensor action check each gradient and
each Hessian column. These results establish the complete algebraic
torsion variation of the stated EC--Gaussian-fermion functional, while
the geometry and reference window retain the fixed values stated above.

### Joint torsion and radius variation of the same Gaussian block

A torsion-stationary point at a prescribed radius need not solve the
radius equation. The previous relative determinant subtracts its
zero-torsion value at each radius. This subtraction has zero torsion
derivative, but has a radius derivative. To vary the full determinant,
restore that reference term, or place the identical term in the
geometry action with its stated sign. These two bookkeeping choices
agree only when the same complete functional is used.

Let `eta=log L`, hold `k` fixed and retain the reference domain
`omega^2+d_n(L)^2<Rk^2`. Define

\[
 \begin{gathered}
 A(z)=\frac{z}{1-e^{-z/k^2}},\qquad
 \delta_n=(d_n-3\tau/(4L))^2-d_n^2,\\
 F^{\rm full}(\tau,L)
 =-\frac1{\pi V_3}\sum_n g_n\int_0^{\Omega_n(L)}
       \log\frac{A(\omega^2+d_n^2)+\delta_n}{k^2}\,d\omega,\\
 \Omega_n^2=Rk^2-d_n^2,\qquad
 F^{\rm ref}(L)=F^{\rm full}(0,L),\qquad
 F^{\rm rel}=F^{\rm full}-F^{\rm ref}.
 \end{gathered}
\]

The logarithm is dimensionless in the same internal scale units. Its
normalization is part of this displayed Gaussian functional. A different
reference subtraction changes the geometry functional by a computable
term and must be propagated into that action. The torsion derivatives
of `F_full` and `F_rel` agree. Their geometry derivatives differ by the
derivative of `F_ref`.

For homogeneous fields it is the integrated action `S=V_3 F` that is
varied, with `V_3=pi^2 L^3`. Thus

\[
 S_\eta=V_3(F_\eta+3F),\qquad
 S_{\tau\eta}=V_3(F_{\tau\eta}+3F_\tau),\qquad
 S_{\eta\eta}=V_3(F_{\eta\eta}+6F_\eta+9F).
\]

The action density alone gives a different radius equation. For example,
the production torsion density is proportional to `L^-2`, whereas its
volume integral is proportional to `L`. In the coordinates `(tau,L)`,
varying the radius at fixed `tau` changes the trace matrix as
`B=(tau/L)I`. These coordinates are nonsingular; joint stationarity is
equivalent to stationarity in the trace matrix and radius coordinates.

Within a fixed open spectral chamber, Leibniz' rule gives the independent
bulk and frequency-edge decomposition

\[
 \begin{split}
 \partial_\eta F^{\rm full}
 ={}&-3F^{\rm full}
 +\frac1{\pi V_3}\sum_n g_n\int_0^{\Omega_n}
       \frac{2(d_n^2 A_z+\delta_n)}{A+\delta_n}\,d\omega\\
 &-\frac1{\pi V_3}\sum_n g_n\frac{d_n^2}{\Omega_n}
       \log\frac{A(Rk^2)+\delta_n}{k^2}.
 \end{split}
\]

The last term is generally nonzero. A finite measurement domain does not
make its Gaussian integrand vanish. At a shell crossing `Omega_n=0`,
this functional generally has a square-root cusp. Ordinary radius
derivatives and Newton boxes are consequently restricted to an open
chamber; the implementation rejects a box meeting a shell crossing.

`fermion_geometry_response` computes the full two-variable Hessian by
differentiating the same integrand and measure. In normalized frequency
coordinates `omega=Omega_n u`,

\[
 z_\eta=-2d_n^2(1-u^2),\quad
 \delta_{n,\eta}=-2\delta_n,\quad
 \partial_\eta\log(\Omega_n/V_3)=d_n^2/\Omega_n^2-3.
\]

These identities give both derivatives and their mixed term. The bulk
and edge formula above provides a separate check. An independent
high-precision frequency integral verifies the resulting geometry force.

For an explicit joint calculation, complete the trace-matched curvature
contribution identified earlier. In the retained units its coefficient
is `gamma=3`; no new coefficient is fitted to a stationary point. On the
isotropic branch the resulting integrated action is

\[
 \boxed{\quad
 S_{\rm test}(\tau,L)
 =\pi^2 L(18-\tfrac92\tau^2)
   +V_3 F^{\rm full}(\tau,L).
 \quad}
\]

The two transverse production terms remain as previously decomposed;
their field equations force both constant trace-free matrices to zero.
This is a specified curvature completion of the production torsion
action. Trace matching fixes its coefficient within this completion;
it does not derive the complete generated matter--geometry action or
its overall normalization. The calculation determines exactly what
this particular completion predicts.

For `k=1,R=5` and three full sixteen-coordinate generations, the two
stationary equations have a numerical solution

\[
 \tau_*=0.11619682549993063,\qquad
 L_*=1.7956264727915705.
\]

The search chamber is bounded by the neighbouring shell thresholds
`3.5/sqrt(5)<L<4.5/sqrt(5)`. At the solution the gradient in `(tau,eta)`
is approximately `(1.1e-14,2.3e-13)`. Its Hessian is approximately

\[
 \begin{pmatrix}
 -150.6485901&71.5623638\\
 71.5623638&3386.9570847
 \end{pmatrix}.
\]

Eliminating the auxiliary trace direction gives the positive radius
Schur curvature `3420.9512423` in the `eta` coordinate. This is a
joint stationary point, not a minimum in the auxiliary torsion variable.
The neutral right reference multiplicity is `42`; the neutral spin
response is retained throughout.

### Rational existence and uniqueness certificate for the joint point

The small numerical gradient is supplemented by a separate interval
proof. Extend the integer-arithmetic kernel with a positive logarithm:
reduce its argument to `[1,2]` by powers of two, put
`z=(x-1)/(x+1)` and use

\[
 \log x=2\sum_{j=0}^{49}\frac{z^{2j+1}}{2j+1}+r,
 \qquad
 0\leq r\leq\frac{2(1/3)^{101}}{101(1-1/9)}.
\]

Together with the existing exponential, square-root and pi enclosures,
this bounds the continuous frequency integrals and the full Hessian
on a two-dimensional parameter box. The integration cells are interval
rectangles, rather than point samples.

Write `g=grad S_test` and choose a rational nonsingular matrix `P`
approximating the inverse Hessian at a rational centre `x0`. The
numerical inverse only proposes this rational matrix. All subsequent
inclusions use outward integer arithmetic. For a box `X`, compute

\[
 T(X)\subseteq x_0-Pg(x_0)+(I-PH(X))(X-x_0),\qquad
 \|I-PH(X)\|_\infty<1.
\]

If the right-hand box lies strictly inside `X`, the map
`T(x)=x-Pg(x)` is a contraction of the complete box into itself.
Banach's theorem gives a unique fixed point; nonsingularity of `P`
makes it a zero of the actual gradient. This proves local existence
and uniqueness independently of the numerical root residual.

For

\[
 X=[0.111,0.122]\times[1.790,1.801]
 \quad\text{in coordinates }(\tau,L),
\]

256 integration cells give a contraction norm below `0.133615`, with
Newton image contained in

\[
 [0.1144939,0.1179039]\times[1.7941224,1.7971579]
 \subset\operatorname{int}X.
\]

The same outward Hessian bounds give `S_tau,tau<0` throughout the box
and radius Schur curvature greater than `936.07` in the `L` coordinate.
Thus the joint two-dimensional auxiliary Hessian has one negative and
one positive direction there. The eight constant trace-free directions
have positive, nonzero production coefficients. Their equations set them
to zero, so the certificate also fixes the stationary point among all
nine homogeneous torsion components and the radius with `(tau,L)` in
this box. It does not classify other spectral chambers or spatially
varying fields.

At the joint solution the reference radius force is about `-328.47020`
and the full frequency-boundary force is about `-593.36077`. Omitting
the reference action changes a zero radius residual to about `328.47020`;
omitting the boundary term changes it to about `593.36077`. These are
direct calculations of the lost terms. At the earlier fixed radius
`L=2.4935343325226915`, the certified torsion saddle instead has radius
residual about `-4578.46600` in the same completed action.

The two-variable calculation therefore does not identify the gauge
content response `1/50` with a connection saddle. It supplies a complete
joint variation and a certified local saddle for an explicit common
block. Matching that block to the generated interacting action still
requires the genuine source vertices behind the two transverse
coefficients and the production spectral insertions. A measured-window
stationary point also depends on its stated boundary response; removing
that response requires carrying the unresolved part in the same action.

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
trace equation has now been solved jointly with the minimal classical
matter equations: it gives zero torsion. A nonzero effective stationary
torsion requires the actual interacting matter action and its computed
condensate. The existing downstream numbers use the gauge-conditioned
`1/50` as their response coordinate. The transfer record includes the
minimal classical result, the nonzero derivative at that coordinate,
and the operator-square mismatch; it does not silently replace the
retained spectrum by a different matter action.

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
coupled classical variation, signed Dirac-square comparison,
profile geometry, loop measure and zero-mode matching without writing
the parameter stores. `tests/test_variational_foundations.py` checks
independent matrix contractions, simultaneous basis changes, numerical
action derivatives in all torsion and matter directions, exact rational
torsion contractions, signed native Dirac squares, Schur/full
resolvent agreement and parameter-parent registration.

`python scripts/solve_torsion_response.py --cells 512` evaluates the
EC--Gaussian-fermion saddle above without writing either parameter
store. `tests/test_torsion_response.py` checks rational square completion
against the nine-direction action, the full auxiliary Schur complement,
the first and second action variations, neutral-line multiplicities,
and continuous-integral enclosures against independent high-precision
integrals. The root certificate uses signs and derivative bounds over
the entire search interval, rather than a small numerical residual.

`python scripts/solve_torsion_response.py --joint-radius-bracket 1.65 1.95 --cells 256`
solves the two joint equations above and checks an outward invariant
Newton box. `tests/test_torsion_geometry.py` compares both gradients
and every Hessian column with independent action variations, checks the
moving boundary against a high-precision frequency integral, and verifies
the rational inclusion and its explicit failure on an unresolved box.
The fixed-radius mode also reports the geometry residual of that saddle.

`cg_core/connection_action.py` computes the complete connection contraction,
its divergence, the signed spin-connection convention and the minimal
non-Abelian gauge cancellation. `tests/test_connection_action.py`
checks every coefficient of the quadratic tensor identity by rational
polarization on all nine components, every covariant-derivative direction,
a nontrivial rational frame rotation and direct connection-matrix
commutators. The same tests compare the actual two-sign determinants
before and after the proposed averaging.

The three action-level matching tasks are consequently explicit:

| Quantity | Computed result | Remaining action identity |
|---|---|---|
| `tau` | Full-carrier gauge response `1/50`; minimal classical stationary torsion `0`; induced four-fermion coefficient `1/32`; the fixed-radius nine-component saddle; a certified local joint torsion/radius saddle near `(0.116197,1.795626)` for the explicit trace-matched curvature/fermion action, including reference, volume and frequency-edge variations; an exact coefficient-span obstruction for the minimal operators | Derive the extra transverse-action coefficients and production response insertions from the actual interacting source vertices; match the common geometry/matter functional and its boundary response |
| `4/27` | Unique survival-profile maximum; Gaussian action derivative differs | Derive the endpoint from the actual effective-action variation and normalize its TT kinetic vertex |
| Gauge factor | Constant-mode integral and exact required `g7^2`; production convention registered | Derive that higher-dimensional kinetic coefficient from the common generated action |

These identities are not replaced by numerically setting an action's
coefficients to the desired response values.
