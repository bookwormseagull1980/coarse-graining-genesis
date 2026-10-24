# Source curvature response

The Coarse Graining Genesis Framework retains the original 120 Gaussian
connection coefficients. Their intensity N has mean q and variance 2q²/120.
The normalized intensity score has third moment sqrt(8/120) and fourth
moment 3+12/120. The finite Gamma polynomial tests retain both corrections.

The complete colour-curvature observable Q has orthogonal Hermite weights
W2, W3 and W4. Its coefficient-composition covariance is

    C_Q(t) = W2 exp(-2 omega |t|) + W3 exp(-3 omega |t|)
             + W4 exp(-4 omega |t|).

These rates use the original coefficient-composition parameter. The radial
restoring mass belongs to the stationary source-family response. Both are
reported separately in `native_colour_source_response`.

## Joint static response

For W(h,J)=log E exp(hN-JQ), partial Legendre transformation in h gives Gamma.
At zero J its fixed-mean curvature is Gamma_JJ=-(W3+W4). Continuing the
existing potential F by

    Phi(n,J) = F(n) + Gamma(n,J) - Gamma(n,0)

gives the stationary mean derivative n'(0+)=-O'(q)/F''(q). The curvature
susceptibility measured after relaxation is

    chi_static = W3+W4 + O'(q)^2/F''(q)
               = W3+W4 + b_Q^2/m_rad^2.

The output `joint_static_susceptibility` records the direct, collective and
total terms, along with the stationary mean derivative. The input Hessian
must satisfy m_rad²=(2q²/120)F''(q). No fitted coefficient is introduced.
The fixed-mean residual includes the fourth radial component as well as
angular contributions; it is not merely a conditional angular variance.

## Precision comparison

For finite conditional centered Gaussians with precisions K_c, the comparison
law has precision E K_c. For a centered Gaussian reference nu,

    E D(nu || nu_c) = D(nu || nu_comp) + C,
    C = (log det E K_c - E log det K_c)/2.

`gaussian_precision_comparison` returns both entropies and the offset. C may
vary with q. The covariance mixture and the comparison Gaussian are distinct.
Independent Gaussian density quadrature tests check the finite identity.

## Proof and verification correspondence

The physical branch of Lean Formalization of Arithmetic and Basic Physical
Interfaces contains `SourceCurvatureSusceptibility` and
`SourceDeterminantCompensation`. The former checks the finite moment
recurrence and the joint-Hessian Schur identities. The latter derives the
unique inverse-determinant correction from the actual source tensor action
and proves preservation of composition and source transport.

The moment recurrence's identification with Gaussian integrals, the analytic
partial Legendre transform, infinite-dimensional source representation and
field reconstruction remain analytic manuscript proofs. The new formal
entries specify their finite coverage in `theorem-index.json`.

Run the focused computation with

    python scripts/verify_source_response.py

It recomputes the generated response at the stored internal radius, runs the
three source-response test modules and writes a scoped result and manifest
under `certificates/source_response`. The production stores and their run
manifest are preserved. The saved result uses binary floating point; its
test record is separate from interval certification and a full production
rerun.
