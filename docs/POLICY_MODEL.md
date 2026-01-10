# Policy Model (SLO-aware)

## Portfolio Note (IP-safe)
This document is generic, safe to publish, and contains no proprietary or patent-related material.

## Goals (SRE-style)
- Meet a deadline target D with measurable risk control.
- Prefer local-first routes when possible.
- Preserve privacy and cost constraints.
- Maintain predictable tail latency behavior (p95/p99).

## Notation
| Symbol | Meaning |
| --- | --- |
| r | candidate route (LOCAL / FALLBACK / DEGRADED) |
| J(r) | multi-objective routing cost for route r |
| w_L, w_C, w_P | weights for latency, cost, privacy terms |
| L_r | measured or estimated latency for route r (ms) |
| C_r | cost proxy for route r (relative units) |
| P_r | privacy risk proxy for route r (relative units) |
| p_miss | probability of missing deadline under route r |
| p95_r, p99_r | tail latency percentiles for route r (ms) |
| alpha, beta | Beta posterior parameters for miss-rate modeling |
| lambda | tail-risk weight or penalty multiplier (if used) |

## Routes
- LOCAL: in-process, local-first handler.
- FALLBACK: alternate route when local is constrained and allowed.
- DEGRADED: minimal response under constraint violation.

## Multi-objective cost function
We model a route r with a weighted cost J(r):

$$
J(r) = w_L * E[L_r] + w_T * TailRisk_r + w_S * P(L_r > D) + w_C * C_r + w_P * P_r
$$

Plaintext:
J(r) = w_L * E[L_r] + w_T * TailRisk_r + w_S * P(L_r > D) + w_C * C_r + w_P * P_r

Choose the best route by minimizing the cost:

$$
 r* = argmin J(r)
$$

Plaintext:
 r* = argmin J(r)

Where:
- E[L_r] is expected latency for route r.
- TailRisk_r summarizes p95/p99 or optional CVaR for route r.
- P(L_r > D) is the deadline miss probability.
- C_r is a cost term (compute, infra, or carbon proxy).
- P_r is a privacy or policy penalty term.
- w_L, w_T, w_S, w_C, w_P are tunable weights.

## Deadline miss probability (Bayesian Beta update)
We treat deadline misses as Bernoulli outcomes for route r. Let s_r be successes (deadline met) and f_r be failures (deadline missed), with a Beta prior Beta(a0, b0).

$$
 p_r ~ Beta(a0 + s_r, b0 + f_r)
$$

Plaintext:
 p_r ~ Beta(a0 + s_r, b0 + f_r)

The posterior mean for the success rate is:

$$
 E[p_r] = (a0 + s_r) / (a0 + b0 + s_r + f_r)
$$

Plaintext:
 E[p_r] = (a0 + s_r) / (a0 + b0 + s_r + f_r)

Approximate miss probability:

$$
 p_miss ~= 1 - E[p_r]
$$

Plaintext:
 p_miss ~= 1 - E[p_r]

Optional conservative choice: use a lower confidence bound of p_r (for example, a lower quantile of the Beta posterior) to reduce the risk of underestimating misses.

## Tail risk (p95/p99) and optional CVaR
TailRisk_r can be expressed using p95 or p99 latency for route r. This captures rare but impactful slow responses.

Optional CVaR (Conditional Value at Risk) description: CVaR at level q summarizes the average latency beyond the q-th percentile (for example, average of the slowest 5 percent). It provides a smoother tail-risk signal than a single percentile while still emphasizing worst-case behavior.

## Weighting guidelines
- Privacy-first: increase w_P and w_S, keep w_C moderate, and allow higher w_L if privacy is critical.
- SLO-first: increase w_S and w_T to prioritize deadline and tail behavior.
- Low-latency: increase w_L and w_T, keep w_C and w_P minimal when allowed.

## Why this matters (portfolio)
A clear policy model explains why a route was chosen, supports audits, and makes SLO tradeoffs explicit without exposing proprietary implementation details.
