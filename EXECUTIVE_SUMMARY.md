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

1. **Ingests** public datasets (USGS, NOAA, AWID, UCI Online Retail) into queryable tables
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
| **Detection Accuracy** | 96.9% (31/32 queries classified correctly) |
| **False Positive Rate** | 0.0% (0/16 baselines flagged) |
| **Recall** | 93.8% (15/16 inefficient queries flagged) |
| **Result-Equivalence Rate** | 93.3% (14/15 flagged rewrites preserved tested-instance results) |
| **Total LLM API Cost** | $0.005522 USD |
| **Queries Evaluated** | 32 (16 baseline, 16 inefficient) |

**Anti-patterns tested:**
- `SELECT *` (unnecessary column projection)
- `missing_predicate` (full table scan without filters)
- `cross_join` (unintended Cartesian product)
- `redundant_subquery` (nested query overhead)
- `non_sargable`, `missing_group_col`, `implicit_coercion`, `missing_limit`
- `or_vs_in`, `union_all`, `like_prefix`, `distinct_group`

---

## Why This Matters (1 minute)

**Why this problem matters:**
- Data warehouses process millions of queries daily
- A single unnoticed cross join in a multi-terabyte warehouse can cost orders of magnitude more than the LLM analysis that catches it
- Manual SQL review does not scale

**Why LLMs are the answer:**
- GPT-4o-mini understands SQL semantics without training data
- No ML pipeline overhead
- Cost per analysis: ~$0.000173 per query in the current 32-query benchmark

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
| Average inefficient risk score | 57.2/100 |
| Separation margin | 42.2 points |

### Rewrite Performance

| Query | Anti-Pattern | Original | Rewritten | Delta | Semantic |
|:------|:-------------|:---------|:----------|:------|:---------|
| USGS - DISTINCT instead of GROUP BY | distinct_group | 7.09ms | 5.14ms | +27.52% | Match |
| NOAA - Cross join variant | cross_join | 272.67ms | 248.87ms | +8.73% | Match |
| AWID - Nested subquery variant | redundant_subquery | 5.36ms | 2.48ms | +53.76% | Match |
| Products - Missing GROUP BY column | missing_group_col | 2.55ms | 2.49ms | +2.38% | Mismatch |

> **Caution:** Measurements use 500-row in-memory DuckDB tables. Millisecond-level differences are useful as instrumentation checks, not production-speedup claims.

---

## Competitive Advantage

| Feature | Our Framework | Rule-Based Systems | Manual Review |
|---------|:-------------|:-------------------|:--------------|
| **Auto-detect anti-patterns** | Yes (96.9% accuracy) | Limited (known patterns) | No |
| **Semantic validation** | Yes (automated) | No | Manual |
| **Cost to run** | ~$0.000173/query | Infrastructure cost | Engineer hours |
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

- **96.9%** detection accuracy
- **0%** false positives
- **93.8%** recall
- **93.3%** tested-instance result-equivalence rate
- **$0.005522** total LLM cost (32 queries)
- **12** SQL anti-pattern types tested
- **5** logical datasets
- **100%** open source

---

**Version:** 2.0 (July 2026)
**Author:** Shouvik Sharma, Data Engineer at Chime
**GitHub:** https://github.com/shouvik-sharma/query-monitoring-framework
