# Changelog

All notable changes to the LLM-Powered Query Monitoring Framework.

## [v2.0] - 2026-07-18

### Changed
- Expanded the benchmark to 5 logical datasets: USGS, NOAA, AWID, products, and orders.
- Replaced synthetic products/orders with UCI Online Retail-derived tables.
- Expanded the workload to 32 queries: 16 baseline and 16 intentionally inefficient variants.
- Expanded anti-pattern coverage to 12 types.
- Updated rewrite validation to use the same real-data DuckDB setup as original query execution.
- Added pre-vs-post runtime columns to `data/cost_analysis_report.md`.

### Metrics (v2.0)
- Detection accuracy: 96.9% (31/32 queries classified correctly)
- False positive rate: 0.0% (0/16 baselines flagged)
- Recall: 93.8% (15/16 inefficient queries flagged)
- Tested-instance result-equivalence rate: 93.3% (14/15 flagged rewrites)
- Total LLM API cost: $0.005522

### Known Limitations
- Pilot-scale evaluation uses 500 rows per table in DuckDB.
- Runtime deltas are instrumentation checks, not production-scale speedup claims.
- AWID redistribution terms remain unconfirmed and should be verified before public archival redistribution.

## [v1.0] - 2026-07-07

### Added
- Public datasets: USGS Earthquake, NOAA Global Hourly, AWID Wi-Fi
- 8-query workload (4 baseline + 4 inefficient with anti-patterns)
- DuckDB execution engine with SQLite history store
- LLM analysis pipeline (GPT-4o-mini) with prompt-based scoring + rewrite
- Semantic validation for rewritten query correctness
- Evaluation report generator with cost tracking
- Single-command reproduction: `python reproduce.py`
- MIT LICENSE and .gitignore
- Full documentation: README.md, ARCHITECTURE.md, CHANGELOG.md

### Metrics (v1.0)
- Detection accuracy: 100% (4/4 inefficient queries identified)
- False positive rate: 0% (4/4 baselines correctly passed)
- Semantic match rate: 75% (3/4 rewrites preserved exact results)
- Total LLM API cost: $0.000671

### Known Limitations
- Pilot-scale evaluation (3 rows per table in DuckDB)
- Benchmark-only — not validated on production warehouses
- Runtime deltas at sub-millisecond scale are measurement noise
