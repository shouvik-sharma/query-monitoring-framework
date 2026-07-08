# Executive Summary: LLM-Powered Query Monitoring Framework

**One-page overview for pitches, conferences, and quick reference**

---

## The Problem (30 seconds)

**Slow and incorrect SQL queries wreak havoc on data operations:**
- Hidden in massive query logs until they cause production incidents
- Manual review & fixing takes 30+ minutes per query
- No real-time feedback to developers
- Requires deep SQL expertise to diagnose and fix

**Current solutions fall short:**
- Query dashboards: Passive, require manual inspection
- Rule-based alerting: High false-positive rate
- Offline ML pipelines: Slow feedback loops, high ops overhead

---

## Our Solution (30 seconds)

**LLM-Powered Query Monitoring Framework**: A lightweight, reproducible system that:

1. **Ingests** public datasets (USGS, NOAA, AWID) into queryable tables
2. **Executes** controlled SQL workloads against DuckDB
3. **Analyzes** each query with an LLM (GPT-4o-mini) for risk scoring
4. **Rewrites** inefficient queries with optimized SQL
5. **Validates** rewrites through automated semantic comparison

**Key innovation:** Open-source, fully reproducible framework for evaluating LLM-based SQL analysis with honest, measured metrics.

---

## Results (1 minute)

**Metrics from benchmark evaluation:**

| Metric | Result |
|--------|--------|
| **Detection Accuracy** | 100% (4/4 inefficient queries identified) |
| **False Positive Rate** | 0% (all baselines correctly passed) |
| **Semantic Match Rate** | 75% (3/4 rewrites preserved exact results) |
| **Total LLM API Cost** | $0.000671 USD |
| **Queries Evaluated** | 8 (4 baseline, 4 inefficient) |

**Anti-patterns tested:**
- `SELECT *` (unnecessary column projection)
- `missing_predicate` (full table scan without filters)
- `cross_join` (unintended Cartesian product)
- `redundant_subquery` (nested query overhead)

---

## Why This Matters (1 minute)

**Why this problem matters:**
- Data warehouses process millions of queries daily
- A single unnoticed cross join in a multi-terabyte warehouse can cost orders of magnitude more than the LLM analysis that catches it
- Manual SQL review does not scale

**Why LLMs are the answer:**
- GPT-4o-mini understands SQL semantics without training data
- No ML pipeline overhead
- Cost per analysis: ~$0.000084 per query

**Why this framework is unique:**
- Fully reproducible using public datasets and open-source tooling
- Honest metrics with documented limitations
- Modular architecture adaptable to any SQL engine

---

## How It Works (1 minute)

```
Public DataSource (CSV)
    ↓
DuckDB Execution Engine
    ↓
query_history.db (SQLite)
    ↓
LLM Analyzer (GPT-4o-mini)
    ↓
Recommendation Engine
    ↓
Report Generator
```

**Key features:**
- Modular: Pluggable data sources and execution engines
- Reproducible: Entire pipeline from public data to measured results
- Transparent: All limitations and caveats documented

---

## Results Detail

### LLM Scoring Accuracy

| Metric | Value |
|--------|-------|
| Average baseline risk score | 15.0/100 |
| Average inefficient risk score | 71.2/100 |
| Separation margin | 56.2 points |

### Rewrite Performance

| Query | Anti-Pattern | Original | Rewritten | Delta | Semantic |
|:------|:-------------|:---------|:----------|:------|:---------|
| USGS - SELECT * | select_star | 0.51ms | 0.65ms | -25.84% | Match |
| USGS - No filter | missing_predicate | 1.01ms | 1.52ms | -50.12% | Match |
| NOAA - Cross join | cross_join | 2.35ms | 1.60ms | +31.82% | Mismatch |
| AWID - Nested subquery | redundant_subquery | 1.21ms | 2.04ms | -68.18% | Match |

> **Caution:** Sub-millisecond measurements reflect Python-to-DuckDB overhead, not query-engine execution cost. The structural value of each rewrite (eliminated cross join, explicit column projection, WHERE predicate) should be evaluated at warehouse scale.

---

## Competitive Advantage

| Feature | Our Framework | Rule-Based Systems | Manual Review |
|---------|:-------------|:-------------------|:--------------|
| **Auto-detect anti-patterns** | Yes (100% accuracy) | Limited (known patterns) | No |
| **Semantic validation** | Yes (automated) | No | Manual |
| **Cost to run** | $0.000084/query | Infrastructure cost | Engineer hours |
| **Reproducible** | Yes (public data) | Varies | No |
| **Open source** | Yes | Rarely | N/A |

---

## Future Work

1. **Expand workload:** Add TPC-H/TPC-DS benchmarks (50-100 queries)
2. **Multi-engine support:** Snowflake, BigQuery, PostgreSQL adapters
3. **Production ingestion:** Real query history from warehouse logs
4. **Multi-model evaluation:** Compare GPT-4, Claude, Llama
5. **Dashboard integration:** Visual query performance trends

---

## Call to Action

**For researchers:**
- Read the full paper: `RESEARCH_PAPER.md`
- Clone and reproduce: `github.com/shouvik-sharma/query-monitoring-framework`
- Build on this work: multi-engine, larger workloads, production validation

**For data engineers:**
- Try the framework on your own datasets
- Contribute new anti-pattern detectors
- Validate rewrites at warehouse scale

---

## Key Numbers (For Pitches)

- **100%** detection accuracy
- **0%** false positives
- **75%** semantic match rate
- **$0.000671** total LLM cost (8 queries)
- **4** SQL anti-patterns tested
- **3** public datasets
- **100%** open source

---

**Version:** 2.0 (July 2026)
**Author:** Shouvik Sharma, Data Engineer at Chime
**GitHub:** https://github.com/shouvik-sharma/query-monitoring-framework
