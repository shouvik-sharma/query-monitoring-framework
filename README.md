# LLM-Powered Query Monitoring Framework

[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.xxxxx-blue)](https://github.com/shouvik-sharma/query-monitoring-framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.0-blue)](https://github.com/shouvik-sharma/query-monitoring-framework/releases/tag/v1.0)

Reproducible evaluation of LLM-based SQL query analysis and optimization.

**Cite this work:**
> S. Sharma, "LLM-Powered Query Monitoring and Optimization Using Reproducible External Data Workloads," v1.0, Jul. 2026. [Online]. Available: https://github.com/shouvik-sharma/query-monitoring-framework

## Overview

This framework ingests public datasets, executes controlled SQL workloads, analyzes queries with an LLM (OpenAI GPT), generates optimized rewrites, and validates recommendations through automated semantic comparisons.

## Results

| Metric | Value |
|--------|-------|
| Detection accuracy | 100% |
| False positive rate | 0% |
| Semantic match rate | 75% |
| Total LLM API cost | $0.000671 |
| Queries evaluated | 8 (4 baseline, 4 inefficient) |

Full report: `data/cost_analysis_report.md`

## Project Structure

```
├── data/
│   ├── raw/                  # Public dataset CSVs
│   │   ├── usgs/             # USGS earthquake data
│   │   ├── noaa/             # NOAA weather data
│   │   └── kaggle_wifi/      # Wi-Fi network frames
│   ├── query_history.db      # SQLite database (7 tables)
│   ├── cost_analysis_report.md
│   ├── query_workload.json
│   └── dataset_manifest.json
├── schema/
│   └── query_history_schema.sql
├── scripts/
│   ├── maintain_datasets.py  # Download/verify public datasets
│   ├── create_db.py          # Initialize SQLite query history database
│   ├── create_query_workload.py  # Generate baseline + inefficient queries
│   ├── execute_query_workload.py # Run queries against DuckDB
│   ├── llm_analysis.py       # LLM scoring + rewrite pipeline
│   ├── generate_report.py    # Produce evaluation report
│   └── cost_analysis_report.py   # CLI wrapper for report output
├── reproduce.py              # One-command reproduction script
├── requirements.txt          # Python dependencies (duckdb, openai)
├── research_progress.md      # Living session log
├── RESEARCH_PAPER.md         # Research paper draft
├── ARCHITECTURE.md           # System architecture
└── CHANGELOG.md              # Version history
```

## Prerequisites

- Python 3.10+
- OpenAI API key (optional — simulated fallback available)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (optional — simulation mode works without it)
set OPENAI_API_KEY=sk-...
```

## Reproduction (Reviewer Quick-Start)

**Paper reference:** [v1.0](https://github.com/shouvik-sharma/query-monitoring-framework/releases/tag/v1.0)

```bash
git clone https://github.com/shouvik-sharma/query-monitoring-framework.git
cd query-monitoring-framework
pip install -r requirements.txt
python reproduce.py
```

To reproduce the full evaluation in one command:

```bash
python reproduce.py
```

This runs all six pipeline stages sequentially:
1. Download public datasets (USGS, NOAA, AWID)
2. Initialize the query history database (schema from `schema/query_history_schema.sql`)
3. Generate 8-query workload (4 baseline + 4 inefficient)
4. Execute queries against DuckDB, store metrics
5. Run LLM analysis + optimized rewrites
6. Generate evaluation report

To skip dataset download if you already have `data/raw/`:

```bash
python reproduce.py --skip-datasets
```

## Manual Step-by-Step

If you prefer to run each stage independently:

```bash
# 1. Acquire datasets
python scripts/maintain_datasets.py sync

# 2. Initialize database
python scripts/create_db.py

# 3. Generate query workload
python scripts/create_query_workload.py

# 4. Execute queries and store metrics
python scripts/execute_query_workload.py

# 5. Run LLM analysis + generate recommendations
python scripts/llm_analysis.py

# 6. Generate evaluation report
python scripts/generate_report.py
```

## Datasets

| Source | Records | Description |
|--------|---------|-------------|
| [USGS Earthquake Feed](https://earthquake.usgs.gov/) | 10,631 | Recent seismic events |
| [NOAA Global Hourly](https://www.ncei.noaa.gov/) | 6,040 | Hourly weather readings |
| [AWID Wi-Fi](https://github.com/krishanuskr/AWID-Intrusion-Detection-System-2020) | 211,190 | Network traffic frames |

## Database Schema

`query_history.db` contains 7 tables:

- `workloads` — Experiment run groupings
- `datasets` — Data source metadata
- `queries` — SQL queries (baselines + inefficient variants)
- `query_executions` — Runtime metrics and status
- `llm_analyses` — Risk scores, issues, token costs
- `recommendations` — Generated rewrites
- `cost_comparisons` — Before/after comparisons

## Anti-Patterns Tested

- `SELECT *` — Unnecessary column projection
- `missing_predicate` — Full table scan without filters
- `cross_join` — Unintended Cartesian product
- `redundant_subquery` — Layered nested query overhead

## Limitations

- Pilot-scale evaluation (3 rows per table) isolates detection/correctness from dataset effects; runtime deltas are measurement noise
- Benchmark-only evaluation — not validated on production warehouses
- SQLite for prototyping — not designed for production query volumes
- Full CSV datasets (10k–211k records) are archived for replication at warehouse scale

## License

MIT. See `LICENSE`.
