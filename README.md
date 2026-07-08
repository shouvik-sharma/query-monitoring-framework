# LLM-Powered Query Monitoring Framework

Reproducible evaluation of LLM-based SQL query analysis and optimization.

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
│   ├── create_query_workload.py  # Generate baseline + inefficient queries
│   ├── execute_query_workload.py # Run queries against DuckDB
│   ├── llm_analysis.py       # LLM scoring + rewrite pipeline
│   └── generate_report.py    # Produce evaluation report
├── research_progress.md      # Living session log
├── RESEARCH_PAPER.md         # Research paper draft
└── ARCHITECTURE.md           # System architecture
```

## Prerequisites

- Python 3.10+
- OpenAI API key (optional — simulated fallback available)

## Setup

```bash
# Install dependencies
pip install duckdb openai

# Set API key (optional — simulation mode works without it)
set OPENAI_API_KEY=sk-...
```

## Usage

```bash
# 1. Acquire datasets
python scripts/maintain_datasets.py sync

# 2. Generate query workload
python scripts/create_query_workload.py

# 3. Execute queries and store metrics
python scripts/execute_query_workload.py

# 4. Run LLM analysis + generate recommendations
python scripts/llm_analysis.py

# 5. Generate evaluation report
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

- Small dataset (3 rows per table) results in sub-millisecond noise for runtime comparisons
- Benchmark-only evaluation — not validated on production warehouses
- SQLite for prototyping — not designed for production query volumes

## License

MIT. See `LICENSE`.
