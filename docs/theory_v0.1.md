# Wave-Induced Observability Shell — Theory Note v0.1

## Status

WIOS v0.1 is a phenomenological stochastic toy model. It is neither a quantum
field theory nor evidence for new physics. Its purpose is to turn one speculative
postulate into explicit assumptions, observables, competitors, and failure
conditions.

## Central postulate

For a subset of weakly coupled excitations, the wave state sources a bounded
observability variable `σ`. Interactions associated with measurement can drive
`σ` upward. A high-`σ` state suppresses localized direct interactions more
strongly than it suppresses a residual coherent channel.

The model further permits high `σ` to increase a latent variable `q`, interpreted
as effective occupancy outside the directly observed brane. This interpretation
is conjectural; in v0.1, `q` is a bounded state variable rather than a spatially
resolved extra-dimensional wavefunction.

## State variables

| Symbol | Range | Meaning |
|---|---:|---|
| `Φ(t)` | real/complex | weak coherent excitation |
| `σ(t)` | `[0, 1]` | observability-shell strength |
| `q(t)` | `[0, 1]` | phenomenological bulk occupancy |
| `M(t)` | `[0, 1]` | controlled measurement strength |
| `I(t)` | non-negative | detector saturation state in the null model |

## WIOS dynamics

The shell evolves according to

```math
d\sigma = f(\sigma, |\Phi|^2, M)dt + \eta dW_t,
```

with

```math
f = -2\kappa\sigma(1-\sigma)(1-2\sigma)
  + a_\Phi |\Phi|^2(1-\sigma)
  + a_M M(t)(1-\sigma)
  - \gamma\sigma.
```

The nonlinear term makes transitions sharp without requiring a discontinuity.
The relaxation term returns the shell toward its low state after measurement.
The implementation bounds the result to `[0, 1]`; replacing this numerical bound
with dynamics derived from a stable action is a mandatory future gate.

Effective bulk occupancy follows

```math
\dot q = k_{in}\,S\!\left(\frac{\sigma-\sigma_c}{T}\right)(1-q)-k_{out}q,
```

where `S` is a logistic function. The return flux is

```math
J_{return}=k_{out}q.
```

## Observation model

The direct and residual channels are intentionally inequivalent:

```math
g_d(\sigma,q)=e^{-\alpha\sigma^2}(1-q),
```

```math
g_w(\sigma,q)=\frac{1-\beta_q q}{1+\beta_\sigma\sigma^2}.
```

Direct clicks are Bernoulli samples of a Poisson process:

```math
P(C_t=1)=1-\exp[-r_d g_d(\sigma_t,q_t)\Delta t].
```

The observed continuous trace is

```math
y_t=A g_w(\sigma_t,q_t)\sin(2\pi f t)
+A_eJ_{return}\sin(2\pi f t-\varphi_e)
+n_t+G_t,
```

where `n_t` contains white and colored noise and `G_t` contains sparse glitches.

## Instrumental null

The competitor has no shell and no bulk. Measurement drives detector saturation:

```math
\dot I = a_I M(t)-I/\tau_I.
```

Both channels are attenuated by the same factor:

```math
g_d^{(0)}=g_w^{(0)}=e^{-I}.
```

This null can produce measurement-correlated silence and recovery. Therefore,
those patterns alone do not distinguish WIOS.

## Primary discriminant

The first discriminant is a channel-asymmetry statistic:

```math
R =
\frac{\text{post-measurement direct visibility}}
     {\text{post-measurement coherent-wave visibility}}.
```

WIOS requires a reproducible regime with `R < 1` while phase coherence remains
above a preregistered threshold. The instrumental null naturally tends toward
`R = 1`.

## What the current simulation establishes

It establishes only constructive consistency at the stochastic state-space
level: a bounded numerical system can be configured to generate shell pulses,
direct-channel suppression, residual coherence, effective bulk occupancy, and
recovery.

It does not establish:

- that the postulate follows from quantum mechanics;
- that `σ` is a physical field;
- that `q` is an actual extra-dimensional coordinate;
- that the parameter values correspond to any known particle;
- that unexplained experimental noise supports the hypothesis.

## Required route to v0.2

1. Define likelihoods for WIOS and multiple detector nulls.
2. Recover hidden parameters from synthetic blinded data.
3. Run identifiability and simulation-based calibration studies.
4. Preregister pulse schedules and evaluation metrics.
5. Add ablations for shell, bulk, backaction, colored noise, and glitches.
6. Penalize model complexity when comparing predictive performance.

## Required route to a field model

A future formulation should introduce fields `Φ(x,w,t)` and `σ(x,w,t)` through
an action, derive rather than prescribe their coupling, specify gauge and Lorentz
properties, conserve probability and stress-energy, and demonstrate freedom from
ghosts, uncontrolled superluminality, and vacuum instability. Only then can `q`
be replaced by probability flow in an explicit extra dimension.
