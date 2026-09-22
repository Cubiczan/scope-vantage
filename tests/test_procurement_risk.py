"""Focused tests for generic procurement risk and value-pool analytics."""
import pytest

from src.analytics.procurement_risk import (
    calculate_risk_adjusted_value_pool,
    calculate_supplier_hhi,
    score_freight_risk,
    score_policy_risk,
    score_price_risk,
)


def test_supplier_hhi_is_scale_independent():
    assert calculate_supplier_hhi({"A": 50, "B": 30, "C": 20}) == 3800.0
    assert calculate_supplier_hhi({"A": 5_000, "B": 3_000, "C": 2_000}) == 3800.0


def test_supplier_hhi_empty_and_invalid_inputs():
    assert calculate_supplier_hhi({}) == 0.0
    with pytest.raises(ValueError):
        calculate_supplier_hhi({"A": 0, "B": 0})
    with pytest.raises(ValueError):
        calculate_supplier_hhi({"A": -1, "B": 2})


def test_risk_scores_are_deterministic_and_capped():
    assert score_price_risk(10, 10) == 50.0
    assert score_price_risk(100, 100) == 100.0
    assert score_freight_risk(25, 50) == 50.0
    assert score_policy_risk(12.5, 50) == 50.0


def test_risk_adjusted_value_pool_uses_all_risk_components():
    result = calculate_risk_adjusted_value_pool(
        1_000_000,
        price_risk_score=20,
        freight_risk_score=40,
        policy_risk_score=60,
        supplier_hhi=2_000,
    )
    assert result == {
        "gross_value_pool": 1_000_000.0,
        "composite_risk_score": 35.0,
        "risk_adjustment": 0.35,
        "risk_adjusted_value_pool": 650_000.0,
    }


def test_risk_adjusted_value_pool_supports_custom_weights():
    result = calculate_risk_adjusted_value_pool(
        100_000,
        price_risk_score=100,
        freight_risk_score=0,
        policy_risk_score=0,
        supplier_hhi=0,
        weights={"price": 1, "freight": 0, "policy": 0, "concentration": 0},
    )
    assert result["composite_risk_score"] == 100.0
    assert result["risk_adjusted_value_pool"] == 0.0


def test_risk_adjusted_value_pool_validates_scores_and_weights():
    with pytest.raises(ValueError):
        calculate_risk_adjusted_value_pool(
            100,
            price_risk_score=101,
            freight_risk_score=0,
            policy_risk_score=0,
        )
    with pytest.raises(ValueError):
        calculate_risk_adjusted_value_pool(
            100,
            price_risk_score=0,
            freight_risk_score=0,
            policy_risk_score=0,
            weights={"price": 0, "freight": 0, "policy": 0, "concentration": 0},
        )
