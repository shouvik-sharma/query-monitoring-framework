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
- `scripts/cost_analysis_report.py`: cost and result-equivalence report generation.
- `scripts/reproduce.py`: end-to-end reproduction entry point.

Reproducibility claim:

- The current artifact reproduces an expanded pilot evaluation with 5 datasets, 32 queries, 96.9% detection accuracy, 0% false positives on baseline queries, 93.8% recall, 93.3% tested-instance result-equivalence rate for rewrites, and $0.005522 total LLM API cost.

Important caveat:

- The current experiment uses 500-row pilot tables. It is a reproducibility and governance artifact, not a production-scale performance benchmark.
