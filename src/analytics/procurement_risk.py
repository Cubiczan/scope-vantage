"""Deterministic procurement risk and value-pool analytics.

The functions in this module operate on already-prepared procurement inputs.
They deliberately do not fetch data or make assumptions about a customer,
category, currency, or supplier market.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Optional


def _bounded_score(value: float, ceiling: float) -> float:
    """Convert a non-negative input to a 0-100 score."""
    if not math.isfinite(value) or value < 0:
        raise ValueError("risk inputs must be finite and non-negative")
    if ceiling <= 0 or not math.isfinite(ceiling):
        raise ValueError("risk ceilings must be positive and finite")
    return min(value / ceiling * 100.0, 100.0)


def _weighted_score(first: float, second: float) -> float:
    return round(0.6 * first + 0.4 * second, 2)


def calculate_supplier_hhi(supplier_values: Mapping[str, float]) -> float:
    """Calculate the supplier Herfindahl-Hirschman Index on a 0-10,000 scale.

    Values may be spend, units, or another consistent exposure measure. They
    are normalized to shares before squaring, so the result is independent of
    the input unit. Empty input returns 0.0; negative, non-finite, or zero-total
    exposures are rejected.
    """
    if not supplier_values:
        return 0.0
    values = list(supplier_values.values())
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("supplier values must be finite and non-negative")
    total = sum(values)
    if total <= 0:
        raise ValueError("supplier values must have a positive total")
    return round(sum((value / total * 100.0) ** 2 for value in values), 2)


def score_price_risk(
    price_change_pct: float,
    volatility_pct: float = 0.0,
    *,
    change_ceiling_pct: float = 20.0,
    volatility_ceiling_pct: float = 20.0,
) -> float:
    """Score price exposure from absolute movement and volatility (0-100).

    The movement contributes 60% and volatility contributes 40%. Each input is
    capped at its ceiling, making the result stable across extreme scenarios.
    """
    return _weighted_score(
        _bounded_score(abs(price_change_pct), change_ceiling_pct),
        _bounded_score(volatility_pct, volatility_ceiling_pct),
    )


def score_freight_risk(
    freight_change_pct: float,
    disruption_probability_pct: float = 0.0,
    *,
    change_ceiling_pct: float = 50.0,
) -> float:
    """Score freight exposure from cost movement and disruption probability."""
    return _weighted_score(
        _bounded_score(abs(freight_change_pct), change_ceiling_pct),
        _bounded_score(disruption_probability_pct, 100.0),
    )


def score_policy_risk(
    tariff_rate_pct: float = 0.0,
    policy_probability_pct: float = 0.0,
    *,
    tariff_ceiling_pct: float = 25.0,
) -> float:
    """Score policy exposure from tariff rate and policy-event probability."""
    return _weighted_score(
        _bounded_score(tariff_rate_pct, tariff_ceiling_pct),
        _bounded_score(policy_probability_pct, 100.0),
    )


def calculate_risk_adjusted_value_pool(
    gross_value_pool: float,
    *,
    price_risk_score: float,
    freight_risk_score: float,
    policy_risk_score: float,
    supplier_hhi: float = 0.0,
    weights: Optional[Mapping[str, float]] = None,
) -> dict[str, float]:
    """Apply procurement risk to a gross value pool.

    ``supplier_hhi`` is converted linearly from the standard 0-10,000 HHI
    scale to a 0-100 concentration score. The default composite weights are
    equal across price, freight, policy, and concentration risk. The returned
    value pool is ``gross_value_pool * (1 - composite_score / 100)``.
    """
    if not math.isfinite(gross_value_pool) or gross_value_pool < 0:
        raise ValueError("gross_value_pool must be finite and non-negative")
    if not math.isfinite(supplier_hhi) or not 0 <= supplier_hhi <= 10_000:
        raise ValueError("supplier_hhi must be between 0 and 10,000")

    scores = {
        "price": price_risk_score,
        "freight": freight_risk_score,
        "policy": policy_risk_score,
        "concentration": supplier_hhi / 100.0,
    }
    if any(not math.isfinite(score) or not 0 <= score <= 100 for score in scores.values()):
        raise ValueError("risk scores must be between 0 and 100")

    applied_weights = dict(weights or {name: 0.25 for name in scores})
    if set(applied_weights) != set(scores) or any(
        not math.isfinite(weight) or weight < 0 for weight in applied_weights.values()
    ):
        raise ValueError("weights must contain non-negative finite values for every risk")
    weight_total = sum(applied_weights.values())
    if weight_total <= 0:
        raise ValueError("weights must have a positive total")

    composite_score = round(
        sum(scores[name] * applied_weights[name] for name in scores) / weight_total,
        2,
    )
    adjustment = round(composite_score / 100.0, 4)
    return {
        "gross_value_pool": round(gross_value_pool, 2),
        "composite_risk_score": composite_score,
        "risk_adjustment": adjustment,
        "risk_adjusted_value_pool": round(gross_value_pool * (1.0 - adjustment), 2),
    }
