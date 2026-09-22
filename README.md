# Scope.Vantage — Supply Chain Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Native-orange.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

**Scope.Vantage** is a comprehensive supply chain intelligence platform built on AWS native services. It ingests global trade data from UN Comtrade, commodity prices from AlphaVantage and FRED, and uses Amazon Bedrock (Claude Haiku) to generate actionable intelligence briefings about supply chain risks, tariff impacts, and strategic opportunities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ UN Comtrade  │  │ AlphaVantage │  │  FRED Economic Data  │  │
│  │ (Trade Flows)│  │ (Commodities)│  │  (Macro Indicators)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼─────────────────────┼──────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA (INGESTION)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  comtrade_ingestion_handler.py — EventBridge schedule      │ │
│  │  - Fetches Comtrade trade flows for critical minerals      │ │
│  │  - Writes raw data to S3 as Iceberg tables                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAKE (S3 + ICEBERG)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ trade_flows │  │ commodity    │  │ supply_chain           │ │
│  │ _raw        │  │ _prices      │  │ _risk_scores           │ │
│  ├─────────────┤  ├──────────────┤  ├────────────────────────┤ │
│  │ trade_flows │  │ logistics    │  │ intelligence           │ │
│  │ _cleaned    │  │ _events      │  │ _briefings             │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────┬──────────────────┬──────────────────┬─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AWS GLUE ETL PIPELINE                           │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │ trade_flow    │  │ commodity      │  │ supply_chain     │   │
│  │ _etl.py       │  │ _etl.py        │  │ _etl.py          │   │
│  │ - Clean raw   │  │ - Price trends │  │ - Risk scoring   │   │
│  │ - HS resolve  │  │ - Volatility   │  │ - Chain graphs   │   │
│  │ - Unit conv.  │  │ - Currency conv│  │ - Bottlenecks    │   │
│  └───────────────┘  └────────────────┘  └──────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP FUNCTIONS (ANALYSIS ORCHESTRATION)             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Compute Risk Scores (SupplyChainService)               │ │
│  │  2. Analyze Tariff Impacts (TariffService)                 │ │
│  │  3. Generate AI Briefings (Bedrock Converse API)           │ │
│  │  4. Write Results to Iceberg Tables                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AMAZON ATHENA (QUERY ENGINE)                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ critical_mineral │  │ tariff_impact    │  │ supply_chain │  │
│  │ _flows.sql       │  │ .sql             │  │ _risk.sql    │  │
│  │ - Bilateral flow │  │ - Active tariffs │  │ - Risk dash  │  │
│  │ - Unit values    │  │ - Impact quant.  │  │ - HHI index  │  │
│  │ - Concentration  │  │ - Trade diversion│  │ - Bottlenecks│  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│               INTELLIGENCE LAYER (BEDROCK AI)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Claude 3 Haiku via Converse API                           │ │
│  │  - Composite Intelligence Scoring                          │ │
│  │  - Narrative Risk Analysis                                 │ │
│  │  - Strategic Recommendations                               │ │
│  │  - Cross-commodity Correlation Insights                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

- **Multi-Source Data Ingestion**: UN Comtrade (via `comtradeapicall`), AlphaVantage, FRED
- **Apache Iceberg Tables**: ACID-compliant table format on S3 with time-travel queries
- **Supply Chain Graph Mapping**: Origin → Processing → Manufacturing → End Market
- **Risk Scoring Engine**: Composite score (Supply 30% + Price Volatility 25% + Logistics 25% + Policy 20%)
- **AI-Powered Analysis**: Claude 3 Haiku generates narrative briefings via Bedrock Converse API
- **Tariff Impact Modeling**: Scenario analysis for trade policy changes
- **Concentration Risk**: Herfindahl-Hirschman Index (HHI) for geographic/supplier analysis
- **Procurement Value Pools**: Deterministic supplier HHI, price/freight/policy risk scores, and risk-adjusted value pools (`docs/PROCUREMENT_RISK_ANALYTICS.md`)
- **Athena Views**: Pre-built analytical views for critical-mineral trade flows, tariff impact, and supply-chain risk (`src/aws/athena_views/`)

## Prerequisites

- Python 3.10+
- AWS account with Bedrock access enabled
- AWS credentials configured (via `.env` or IAM)
- Terraform 1.5+ (for infrastructure deployment)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create a .env with your AWS credentials and API keys
# (e.g., FRED_API_KEY, an AlphaVantage key, and a Comtrade subscription key)
```

### 3. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

The Terraform stack provisions the S3 data lake and Iceberg warehouse, Glue
catalog tables, Athena workgroup, Lambda functions, EventBridge schedules, and
the Step Functions pipeline that computes risk scores, analyzes tariff impacts,
and generates AI briefings on schedule.

### 4. Run Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
scope-vantage/
├── bedrock_client.py           # Bedrock Converse API wrapper
├── requirements.txt            # Python dependencies
├── src/
│   ├── models/                 # Domain models (6)
│   │   ├── trade_flow.py
│   │   ├── commodity.py
│   │   ├── supply_chain_node.py
│   │   ├── logistics_event.py
│   │   ├── tariff_regulation.py
│   │   └── intelligence_briefing.py
│   ├── services/               # Business logic (5)
│   │   ├── comtrade_service.py
│   │   ├── pricing_service.py
│   │   ├── supply_chain_service.py
│   │   ├── tariff_service.py
│   │   └── intelligence_service.py
│   ├── aws/                    # AWS integrations
│   │   ├── glue_scripts/       # ETL scripts (3)
│   │   └── athena_views/       # SQL views (3)
│   └── lambda/                 # Lambda handlers (2)
├── notebooks/                  # package placeholder (no pipeline notebooks committed)
├── terraform/                  # Infrastructure as Code
└── tests/                      # Test suite (50+ tests)
```

## API Usage

### ComtradeService — Trade Data Ingestion

```python
from src.services.comtrade_service import ComtradeService

svc = ComtradeService()
# Fetch lithium trade flows
flows = svc.fetch_trade_flows(
    reporter_code=842,  # Australia
    partner_code=156,   # China
    commodity_code="2836.90",  # Lithium carbonate
    year=2023,
)
```

### PricingService — Commodity Prices

```python
from src.services.pricing_service import PricingService

svc = PricingService()
prices = svc.get_commodity_price("LITHIUM")
```

### IntelligenceService — AI Analysis

```python
from src.services.intelligence_service import IntelligenceService

svc = IntelligenceService()
briefing = svc.generate_briefing(
    scope="commodity",
    focus="Lithium",
    include_recommendations=True,
)
print(briefing.summary)
print(briefing.risk_assessment)
```

## Tracked Commodities (Critical Minerals)

| HS Code     | Commodity        | Category         |
|-------------|------------------|------------------|
| 2836.90     | Lithium Carbonate | Critical Mineral |
| 8105.20     | Cobalt           | Critical Mineral |
| 7504.00     | Nickel           | Critical Mineral |
| 7403.11     | Copper           | Critical Mineral |
| 2846.90     | Rare Earth       | Critical Mineral |

## Intelligence Scoring Formula

```
Composite Score = (
    Supply Risk (HHI-based)        × 0.30 +
    Price Volatility (30d σ/μ)     × 0.25 +
    Logistics Risk (events index)   × 0.25 +
    Policy Risk (tariff weight)     × 0.20
)
```

## AWS Cost Estimates (Monthly)

| Service         | Usage                          | Est. Cost   |
|-----------------|--------------------------------|-------------|
| S3 Storage      | 50 GB Iceberg tables           | ~$1.20      |
| Athena Queries  | 100 queries/month              | ~$5.00      |
| Lambda          | 10K invocations                | ~$0.50      |
| Step Functions  | 500 state transitions          | ~$0.75      |
| Glue ETL        | 3 jobs × 10 min                | ~$1.50      |
| Bedrock (Haiku) | 100K tokens/month              | ~$0.25      |
| EventBridge     | 30 scheduled rules             | ~$0.30      |
| **Total**       |                                | **~$9.50**  |

## Evidence Matrix

Every capability claim in this README and in `docs/` is bound to deterministic
evidence in `evidence/matrix.yaml` and machine-verified on every push and pull
request by `tools/verify_evidence_matrix.py` — fail-closed: CI refuses builds
while any row is unverifiable. Run it locally with:

```bash
python3 tools/verify_evidence_matrix.py
```

## License

MIT

---

## CHP Governance

This repository is hardened with the [Consensus Hardening Protocol (CHP)](https://codeberg.org/cubiczan/consensus-hardening-protocol), Cubiczan's decision-governance layer for multi-agent AI systems.

### Protocol Layers
- **R0 Gate**: All decisions must pass Solvable, Scoped, Valid, Worth_it checks
- **Foundation Disclosure**: 1-3 weakest assumptions, 1-2 invalidation conditions, 1 key vulnerability
- **Adversarial Layer**: Mandatory devil's advocate at Phase 0 and Round 3
- **State Machine**: EXPLORING → PROVISIONAL → PROVISIONAL_LOCK → LOCKED
- **Third-Party Validation**: Independent CONFIRM/REJECT before lock

### Domain Configuration
- **Category**: Mining / Supply Chain
- **Foundation Threshold**: 75
- **CFO Accuracy Guard**: Disabled

### Compliance Artifacts
| File | Purpose |
|------|---------|
| `.chp/STATE_MACHINE.md` | Decision state transitions |
| `.chp/R0_CONFIG.yaml` | Domain-calibrated thresholds |
| `.chp/ADVERSARIAL_PROMPTS.md` | Standardized challenge templates |
| `.chp/CHP_COMPLIANCE.md` | Compliance tracking & audit trail |

### CHP Version
cognitive-mesh-orchestrator 0.1.0 | [Protocol Docs](https://codeberg.org/cubiczan/consensus-hardening-protocol)
