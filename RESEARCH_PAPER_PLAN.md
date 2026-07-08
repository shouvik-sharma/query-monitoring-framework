# Research Paper Plan: LLM-Powered Query Monitoring Framework

## Working Title

LLM-Powered Query Monitoring and Optimization Using Reproducible External Data Workloads

## Core Research Question

Can an LLM-powered monitoring framework identify inefficient or risky SQL queries, recommend improved versions, and produce measurable query-cost improvements when evaluated on reproducible external datasets?

## Current Constraint

No internal production data is available. The research must recreate the monitoring process from external/public or synthetic data and must avoid unsupported production claims.

## Proposed Methodology

1. Select a reproducible dataset such as TPC-H/TPC-DS style benchmark data.
2. Load the dataset into a local SQL execution engine, preferably DuckDB for ease of reproduction or PostgreSQL for broader familiarity.
3. Create a controlled query workload containing baseline queries and intentionally inefficient variants.
4. Execute each query and save execution metadata into `query_history.db`.
5. Analyze query text with an LLM to produce a risk score, issue explanation, and optimized SQL recommendation.
6. Execute the recommended query when safe.
7. Compare original and recommended queries using correctness checks and cost proxies.
8. Generate reports that document runtime improvement, semantic equivalence, failure cases, and LLM API cost.

## Query History Schema Scope

The `query_history.db` database should track:

- Original query text and source dataset
- Query execution status
- Runtime in milliseconds
- Rows returned
- Result checksum or validation sample
- Explain-plan output or cost estimate where available
- LLM model, prompt version, input tokens, output tokens, and estimated API cost
- LLM risk score and issue explanation
- Recommended query text
- Rewritten-query execution metrics
- Before/after improvement percentage
- Semantic match status

## Evaluation Metrics

- Detection rate for intentionally inefficient queries
- Precision of high-risk flags based on manual labels or known injected anti-patterns
- Runtime improvement percentage after rewriting
- Percentage of rewrites that preserve result semantics
- Rewrite failure rate
- LLM cost per analyzed query
- LLM cost per successful improvement
- End-to-end processing latency

## Paper Outline

1. **Abstract**
   Summarize the framework, reproducible evaluation setup, and measured results.

2. **Introduction**
   Explain why query monitoring matters, why manual review does not scale, and why LLMs are promising for SQL analysis.

3. **Problem Statement**
   Define the monitoring problem: ingest query workloads, identify inefficient/risky SQL, recommend improvements, and quantify cost changes.

4. **System Design**
   Present the modular pipeline: data source, execution engine, query-history store, LLM analyzer, recommendation engine, validation runner, and reporting layer.

5. **Implementation**
   Describe the prototype implementation, configuration, database schema, prompts, and execution workflow.

6. **Experimental Setup**
   Describe dataset choice, query workload construction, inefficient-query injection, execution engine, and measurement methodology.

7. **Results**
   Report only measured results from the recreated process: scoring accuracy, rewrite success, runtime/cost deltas, LLM overhead, and failure cases.

8. **Discussion**
   Discuss where LLM recommendations worked, where they failed, and how cost savings compare against LLM API cost.

9. **Limitations**
   Note that the first evaluation is benchmark-based, not production-based. Discuss semantic validation limits, missing business context, and engine-specific behavior.

10. **Future Work**
    Add warehouse adapters, production query-history ingestion, feedback loops, dashboards, and multi-model evaluation.

11. **Conclusion**
    Summarize whether the framework produced practical and measurable query improvements.

## Recommended Immediate Build Order

1. Finalize dataset and execution engine: TPC-H style data on DuckDB is the fastest reproducible path.
2. Implement `query_history.db` schema.
3. Create a small workload of 20-50 queries with labeled inefficiency types.
4. Run original queries and collect metrics.
5. Add LLM scoring and recommendation prompts.
6. Run rewritten queries and compare before/after results.
7. Generate the first `cost_improvement_report.md`.
8. Start `RESEARCH_PAPER.md` once the first measured results exist.

## Claims To Avoid Until Measured

- Production-ready
- 95% precision
- 90% rewrite correctness
- Less than 6 second latency
- Three months of production use
- Specific dollar savings

These can be replaced with measured benchmark results after the recreated evaluation pipeline runs.
