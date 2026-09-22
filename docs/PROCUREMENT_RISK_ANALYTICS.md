# Procurement Risk Analytics

`src.analytics.procurement_risk` provides pure, deterministic calculations
for generic procurement analysis. Inputs are supplied by the caller; the
module does not access external data or credentials.

## Calculations

- `calculate_supplier_hhi` normalizes supplier spend, volume, or exposure into
  shares and returns the standard HHI on a 0-10,000 scale.
- `score_price_risk` combines absolute price movement (60%) and volatility
  (40%), with each input capped at its configured ceiling.
- `score_freight_risk` combines freight-cost movement (60%) and disruption
  probability (40%).
- `score_policy_risk` combines tariff/policy cost (60%) and policy-event
  probability (40%).
- `calculate_risk_adjusted_value_pool` converts HHI to a 0-100 concentration
  score, combines it with the three component scores, and applies the resulting
  risk factor to the gross value pool. The default weights are equal and can be
  replaced with a complete `price`, `freight`, `policy`, and `concentration`
  mapping.

All scores are bounded to 0-100, outputs are rounded for stable reporting, and
invalid negative, non-finite, or zero-total inputs raise `ValueError`.
