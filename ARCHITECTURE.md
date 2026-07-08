# Architecture: LLM-Powered Query Monitoring Framework

## Overview

This document describes the architecture of the refactored LLM-Powered Query Monitoring Framework. The first research prototype should not depend on private production data. It should use external/public or synthetic datasets, execute a reproducible SQL workload, persist query executions to a local `query_history` database, ask an LLM to analyze and rewrite problematic queries, then measure before/after cost improvements.

## System Components

### 1. Data Source Layer
- **Generic DataSource Interface**: Abstract interface for all data sources
- **DataSource Adapters**: Implementations for specific data sources:
  - CSV/JSON file readers
  - Database connectors (PostgreSQL, MySQL, etc.)
  - API clients for cloud services
- **Query Extractor**: Pulls SQL queries from various sources

### 2. Query Storage Layer
- **Query History Database**: Persistent storage for all processed queries
- **Metadata Store**: Stores query metadata, processing timestamps, and results
- **Configuration Store**: Stores system configuration and settings

### 2a. Execution Engine Layer
- **ExecutionEngine Interface**: Runs SQL against a target engine and returns execution metrics
- **Initial Engine**: DuckDB or PostgreSQL for reproducible local evaluation
- **Future Engines**: Snowflake, BigQuery, Redshift, Databricks SQL
- **Metrics Collector**: Captures runtime, rows returned, row-count/checksum validation, explain-plan output, and engine-specific cost estimates where available

### 3. Analysis Engine
- **Query Parser**: Parses SQL queries into structured format
- **LLM Analyzer**: Uses LLM to analyze query correctness and efficiency
- **Scoring Engine**: Assigns risk scores to queries (0-100 scale)
- **Pattern Matcher**: Identifies common query anti-patterns

### 4. Recommendation Engine
- **Query Rewriter**: Generates optimized versions of problematic queries
- **Improvement Suggestions**: Provides human-readable recommendations
- **Cost Estimator**: Calculates measured or estimated savings from optimizations
- **Validation Runner**: Executes original and rewritten queries when safe and compares result equivalence

### 5. Reporting & Interface Layer
- **CLI Interface**: Command-line interface for system interaction
- **Web Dashboard**: (Future) Web interface for monitoring and reports
- **Alert System**: Notification system for critical issues
- **Export Module**: Export recommendations and metrics

## Data Flow

```mermaid
graph LR
    A[External Data Sources] --> B[DataSource Adapters]
    B --> C[Query Extractor]
    C --> D[Execution Engine]
    D --> E[Query History Database]
    E --> F[LLM Analyzer]
    F --> G[Scoring Engine]
    G --> H{High Risk?}
    H -->|Yes| I[Recommendation Engine]
    H -->|No| J[Logging]
    I --> K[Validation Runner]
    K --> L[Cost Comparison]
    L --> M[Report Generation]
    M --> N[Output Reports]
```

## Module Details

### DataSource Interface
```python
class DataSource:
    def connect(self):
        """Establish connection to data source"""
        pass
    
    def extract_queries(self):
        """Extract SQL queries from source"""
        pass
    
    def validate_connection(self):
        """Validate that connection is working"""
        pass
```

### Query History Database Schema
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    query_text TEXT NOT NULL,
    source_type TEXT,
    source_identifier TEXT,
    extracted_at TIMESTAMP,
    processed_at TIMESTAMP
);

CREATE TABLE query_executions (
    id INTEGER PRIMARY KEY,
    query_id INTEGER,
    execution_label TEXT, -- original or rewritten
    engine TEXT,
    status TEXT,
    runtime_ms INTEGER,
    rows_returned INTEGER,
    result_checksum TEXT,
    explain_plan TEXT,
    estimated_cost REAL,
    executed_at TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

CREATE TABLE query_scores (
    query_id INTEGER,
    score INTEGER,
    score_reason TEXT,
    processed_at TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

CREATE TABLE recommendations (
    query_id INTEGER,
    recommended_query TEXT,
    improvement_reason TEXT,
    estimated_savings TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

CREATE TABLE cost_comparisons (
    query_id INTEGER,
    original_runtime_ms INTEGER,
    rewritten_runtime_ms INTEGER,
    runtime_improvement_pct REAL,
    semantic_match BOOLEAN,
    llm_input_tokens INTEGER,
    llm_output_tokens INTEGER,
    llm_cost_usd REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);
```

### LLM Analysis Prompts
The system will use structured prompts for different analysis tasks:

1. **Query Scoring Prompt**:
   ```
   Score this SQL query for correctness and efficiency on a scale of 0-100:
   - 0-20: Excellent/optimized queries
   - 21-40: Good with minor inefficiencies
   - 41-60: Moderate issues
   - 61-80: Significant problems
   - 81-100: Critical issues (needs immediate attention)
   
   Query: {sql_query}
   
   Return ONLY JSON: {"score": <number>, "reason": "<brief explanation>"}
   ```

2. **Query Rewriting Prompt**:
   ```
   You are a SQL optimization expert. Rewrite the following query to improve its performance and correctness.
   If the query is already optimal, return the original query.
   
   Original Query: {sql_query}
   
   Return ONLY the optimized SQL query:
   ```

## Configuration

The system will be configurable via a YAML configuration file:

```yaml
data_sources:
  - type: csv
    path: ./queries.csv
    query_column: sql_text
  - type: postgresql
    connection_string: postgresql://user:pass@host:port/db
    query: SELECT query_text FROM query_log

llm:
  provider: openai
  model: gpt-4
  api_key_env: OPENAI_API_KEY

storage:
  type: sqlite
  path: ./query_history.db

execution:
  engine: duckdb
  database_path: ./benchmark.duckdb

analysis:
  high_risk_threshold: 80
  medium_risk_threshold: 60
```

## Evaluation Dataset Strategy

The first paper-quality experiment should use a reproducible dataset and workload:

1. **Preferred benchmark:** TPC-H or TPC-DS style data, generated locally or loaded into DuckDB/PostgreSQL.
2. **Workload:** A mix of canonical benchmark queries and intentionally inefficient variants, such as unnecessary `SELECT *`, missing predicates, non-sargable filters, avoidable cross joins, repeated subqueries, and inefficient aggregations.
3. **Measurement:** Execute original queries, store metrics, run LLM analysis and rewrite, execute rewritten queries, then compare correctness and cost proxies.
4. **Cost proxies:** Runtime, rows returned, explain-plan estimates, bytes/rows processed where available, and LLM API cost.
5. **Publication constraint:** Only measured results from this recreated process should be used in the paper. Existing placeholder production claims should be removed or clearly marked as hypothetical.

## Future Extensions

1. **Multi-LLM Support**: Integration with Claude, Llama, and other models
2. **Web Dashboard**: Interactive dashboard for monitoring and reports
3. **Real-time Processing**: Continuous monitoring of data sources
4. **Custom Rules Engine**: User-defined query analysis rules
5. **Integration Plugins**: Connectors for Slack, email, and other notification systems
