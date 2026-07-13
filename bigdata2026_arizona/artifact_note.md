# Artifact Note for IEEE BigData 2026

Repository: https://github.com/shouvik-sharma/query-monitoring-framework

Recommended artifact statement for the paper:

> The implementation is released as an open-source artifact containing dataset-maintenance scripts, DuckDB workload execution, the SQLite query-history schema, LLM analysis, rewrite validation, and report generation scripts.

Artifact contents:

- `scripts/maintain_datasets.py`: dataset download and validation.
- `scripts/create_db.py`: query-history database initialization.
- `schema/query_history_schema.sql`: SQLite schema.
- `scripts/execute_query_workload.py`: DuckDB workload execution.
- `scripts/llm_analysis.py`: LLM scoring and recommendation generation.
- `scripts/generate_report.py`: evaluation report generation.
- `scripts/cost_analysis_report.py`: cost and semantic-match report generation.
- `scripts/reproduce.py`: end-to-end reproduction entry point.

Reproducibility claim:

- The current artifact reproduces a pilot-scale evaluation with 3 public datasets, 8 queries, 100% inefficient-query detection for the tested anti-patterns, 0% false positives on baseline queries, 75% semantic-match rate for rewrites, and $0.000671 total LLM API cost.

Important caveat:

- The current experiment uses 3-row pilot tables. It is a reproducibility and governance artifact, not a production-scale performance benchmark.
