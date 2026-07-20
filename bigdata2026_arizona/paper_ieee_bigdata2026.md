# LLM-Powered Query Monitoring and Optimization for Reproducible Big Data Workloads

## Abstract
Big data platforms execute heterogeneous analytical SQL workloads across scientific, operational, and security datasets. Inefficient queries can increase cost, delay downstream analytics, and reduce trust in shared data infrastructure. This paper presents a reproducible framework for LLM-powered query monitoring and optimization. The framework ingests publicly accessible datasets, executes a controlled DuckDB workload, stores query telemetry in SQLite, analyzes SQL with a large language model, records optimization recommendations, and validates rewritten queries through execution-based result checks. In an evaluation over five logical datasets and 32 queries (16 baseline, 16 inefficient) targeting 12 distinct anti-pattern types, the framework achieved 96.9% detection accuracy, 0% false positive rate, 93.8% recall, and a 93.3% tested-instance result-equivalence rate for rewrites, with total LLM API cost of $0.005522. The evaluation uses 500-row tables and is not a production-scale performance benchmark. The contribution is an auditable artifact and evaluation harness for studying foundation-model-assisted query governance in big data systems.

## Keywords
big data systems, query monitoring, SQL optimization, large language models, reproducibility, benchmark artifacts

## Introduction
Big data systems are increasingly used to integrate scientific, environmental, cybersecurity, and operational datasets. As these platforms grow, SQL workloads become more diverse: analysts issue ad hoc queries, dashboards run recurring aggregations, and data applications generate programmatic SQL. Inefficient queries can silently increase runtime, waste compute, and produce avoidable operational cost. Query monitoring is therefore a governance problem as well as a performance problem.

Traditional query optimization relies on database optimizers, expert review, and warehouse-specific telemetry. These mechanisms remain essential, but they do not fully address the human-facing problem of explaining why a query is risky, identifying common anti-patterns, and proposing understandable rewrites. Recent foundation models create an opportunity to augment query review with natural-language reasoning and code transformation. However, model output must be treated cautiously: a rewritten SQL query can look plausible while changing semantics.

This paper presents an LLM-powered query monitoring framework designed for reproducible experimentation. The system downloads public datasets, constructs a controlled workload of 32 queries spanning five datasets and 12 anti-pattern types, executes queries against DuckDB\cite{raasveldt2020duckdb}, records telemetry in a SQLite query-history database\cite{sqlite2026}, analyzes SQL with an LLM, stores recommendations, executes rewritten queries, and reports detection, result-equivalence, runtime, and cost metrics. The framework is open source\cite{sharma2026framework}.

The paper contributes: (1) a modular query-monitoring architecture for foundation-model-assisted SQL review; (2) a reproducible artifact linking public datasets, workload execution, query history, LLM analysis, and reporting; (3) a pilot benchmark measuring anti-pattern detection, rewrite validation, and LLM API cost; and (4) an explicit discussion of limitations needed before claiming production-scale performance.

This work addresses four research questions. **RQ1:** How accurately does LLM-assisted review detect SQL anti-patterns on a labeled pilot workload? **RQ2:** How often do generated rewrites execute successfully and preserve tested-instance results? **RQ3:** What latency and monetary-cost overheads are introduced by LLM-assisted monitoring? **RQ4:** How does performance vary across datasets and anti-pattern categories, and what additional baselines are needed for production-grade claims?

## Related Work
We organize prior work into four themes that jointly motivate the proposed framework and highlight the gap this work addresses.

### SQL Anti-pattern Detection and Static Analysis
A mature ecosystem of static analysis tools exists for identifying risky SQL patterns through deterministic rule-based checks. Tools such as sqlaudit\cite{sqlaudit} detect SELECT *, cross joins, missing WHERE clauses, implicit type coercions, and invalid predicate pushdowns from raw query text. At warehouse scale, Google BigQuery Anti-pattern Recognition\cite{gcpantipattern} scans INFORMATION_SCHEMA for top-slot-consuming jobs, flagging missing partition filters and suboptimal join order through execution statistics. DWH-Auditor\cite{dwhauditor} similarly detects full table scans, zombie tables, and under-utilized materialized views in enterprise data warehouses. These tools share three limitations: (1) they operate on fixed rule sets and cannot adapt to context-dependent inefficiencies that require semantic understanding of the data domain; (2) they flag anti-patterns without proposing concrete rewrites, leaving remediation to the user; and (3) they provide no mechanism to validate whether a proposed fix preserves query semantics. Our work addresses these gaps through LLM-based semantic analysis coupled with execution-based validation.

### LLMs for SQL Optimization and Rewriting
Recent work demonstrates that LLMs can understand SQL semantics and suggest meaningful optimizations. R-Bot\cite{rbot2025} proposes a multi-source rewrite evidence pipeline with hybrid structure-semantics retrieval, achieving state-of-the-art rewrite quality on production Huawei workloads. LLMOpt\cite{llmopt2025} fine-tunes LLMs for plan candidate generation, outperforming traditional optimizers on the Join Order Benchmark by exploring a broader plan space. LLMSTEER\cite{llmsteer2024} shows that LLM embeddings of raw SQL contain sufficient semantic information for a binary classifier to outperform heuristics on plan selection, suggesting that even frozen LLM representations encode query properties relevant to optimization. LaPuda\cite{lapuda2024} introduces a policy-based multi-modal optimizer with a cost descent algorithm that learns from execution feedback. LLM4Hint\cite{llm4hint2025} demonstrates that moderate-sized LLMs (7B parameters) can recommend effective optimizer hints, reducing the need for large models. Despite these advances, existing LLM-based approaches focus narrowly on optimizer hint selection or plan space exploration. Among the systems examined in our review, we did not identify one that jointly persists query telemetry, records structured LLM recommendations, validates generated rewrites through re-execution, and reports per-query model cost.

### Cloud Warehouse Monitoring and Governance
Production cloud data warehouses have motivated significant work on workload monitoring and resource governance. SnowPatrol\cite{snowpatrol2023} applies unsupervised anomaly detection to Snowflake usage metadata, identifying outlier queries by runtime and slot consumption. Keebo\cite{keebo2023} continuously monitors warehouse performance telemetry to automate sizing decisions and auto-suspend intervals, reducing idle compute by up to 40%. Bress et al.\cite{bress2025snowflake} conducted a large-scale empirical study of 667 million production queries from Snowflake, identifying that 62% of queries access fewer than 10 columns and that missing filters are among the most common performance issues. Patterns\cite{patterns2026} extracts historical query patterns to recommend partitioning keys and clustering orders via AI-driven analysis of query access paths. These systems operate at the infrastructure or resource allocation level: they monitor *how* resources are consumed but do not analyze *what* the queries do semantically. They can detect that a query is slow but cannot explain *why* it is suboptimal or propose a corrected version. Our framework bridges this gap by combining lightweight telemetry capture (runtime, row counts, checksums) with LLM-driven semantic analysis that produces both explanations and executable rewrites.

### Benchmarks for Reproducible Evaluation
The database community has established several benchmarks for evaluating query processing and optimization. TPC-H\cite{tpch} and TPC-DS\cite{tpcds} remain the gold standard for measuring analytical query throughput and resource utilization across standardized schemas and data distributions. The Join Order Benchmark (JOB)\cite{leis2015job} provides real-world queries derived from the IMDB dataset, capturing the complexity of multi-way joins with realistic cardinality estimation challenges. BIRD-INTERACT\cite{huo2025bird} introduces a dynamic interaction framework for text-to-SQL evaluation, where the model can issue database exploration queries before generating a final answer. SPIDER\cite{yu2018spider} and its variants provide cross-domain text-to-SQL benchmarks with annotated queries. However, none of these benchmarks targets the specific task of evaluating LLM-based query monitoring frameworks. A suitable benchmark requires: (a) labeled workloads containing both optimal and intentionally inefficient query variants with ground-truth annotations; (b) multiple datasets spanning diverse domains to test cross-domain generalization; (c) execution telemetry (runtime, cardinality, cost) for both original and rewritten queries; and (d) standardized metrics for detection accuracy and result-equivalence rate. Our workload design (Section 5.2) provides a starting point toward such a benchmark.

## System Design and Methodology
The framework implements a modular pipeline that transforms raw SQL queries into structured, validated, and cost-accounted optimization recommendations. Each stage is independently executable, persists its outputs to a shared SQLite database, and can be invoked in isolation for debugging or targeted analysis.

### System Overview and Data Flow
Figure 1 illustrates the six-stage pipeline through which a query travels. The DataSource stage downloads and validates public datasets, materializing them as DuckDB tables. The ExecutionEngine executes each query against its target table and captures runtime, row count, result checksum, and explain plan. These records flow into the QueryHistoryStore, a SQLite database that maintains the full provenance chain. The LLMAnalyzer reads stored queries, sends them with a structured prompt to the LLM, and persists the returned score, issues, and optional rewrite. For flagged queries (score ≥ τ), the RecommendationEngine executes the rewritten query through the same harness, validates tested-instance result equivalence, and computes cost deltas. Finally, the ReportGenerator aggregates all results into detection accuracy, result-equivalence rate, and cost summaries. Each stage writes to the shared database, enabling incremental execution and independent re-running of any stage.

### Problem Formulation
Let a query workload be a set of SQL queries Q = {q₁, ..., qₙ} executed against a dataset d ∈ D on an engine e ∈ E. The execution function

exec(qᵢ, d, e) ↦ Mᵢ = (tᵢ, rᵢ, cᵢ, pᵢ)

produces a metric tuple comprising wall-clock runtime tᵢ (ms), row-count rᵢ, result checksum cᵢ (SHA-256 of sorted result rows), and explain-plan text pᵢ.

The LLM analysis function

f_LLM(qᵢ) ↦ (sᵢ, Iᵢ, q'ᵢ)

assigns a risk score sᵢ ∈ [0, 100], identifies issues Iᵢ = {i₁, ..., iₖ}, and optionally produces a rewritten query q'ᵢ when sᵢ ≥ τ, where τ = 40 is the detection threshold.

The result validation function compares original and rewritten executions. We define resEq(qᵢ, q'ᵢ) as 1 when both the row count and sorted result checksum of the rewritten query match the original execution, and 0 otherwise.

The total LLM API cost is

C_LLM = ∑ (p_in · tok_in⁽ⁱ⁾ + p_out · tok_out⁽ⁱ⁾)

where p_in = $0.15/10⁶ tokens and p_out = $0.60/10⁶ tokens (GPT-4o-mini). We report runtime and cost as separate quantities.

### Pipeline Pseudocode
Algorithm 1 describes the end-to-end monitoring loop. The algorithm takes a dataset list D, workload Q, engine E, and threshold τ as input. It initializes empty sets R and C, then iterates over each query-dataset pair. For each query, it executes the original query, stores the query and execution records, analyzes the query with the LLM, and stores the analysis. If the query is flagged (score ≥ τ), it executes the rewritten query, stores the execution, computes result equivalence, cost delta, and LLM cost, and stores the recommendation and comparison. The algorithm accumulates detection results in R and cost records in C, returning both sets.

### Architectural Components
The architecture is organized as six modular components, each with a clearly defined interface, responsibility, and storage interaction. The components are:

1. **Data source**: Downloads and stages datasets
2. **Execution engine**: Runs SQL and records runtime and checksums
3. **History store**: Maintains the SQLite system of record
4. **LLM analyzer**: Scores queries and stores model output
5. **Recommender**: Rewrites, validates, and measures changes
6. **Report generator**: Summarizes accuracy and cost

Each component maps to one or more repository scripts. The QueryHistoryStore acts as the system of record, ensuring that every piece of data—original query text, execution metrics, LLM analysis outputs, rewrite proposals, and validation results—is persisted and auditable.

## Experimental Setup
The evaluation uses five logical datasets spanning scientific, environmental, cybersecurity, and commercial domains. Three tables come directly from publicly accessible scientific, weather, and wireless-security sources; two retail tables are derived from the UCI Online Retail dataset\cite{chen2015online}. Each table contains 500 sampled rows for the reported pilot run.

The workload comprises 32 SQL queries partitioned into two equal classes: 16 baseline queries that follow best practices, and 16 inefficient variants that each introduce exactly one common database anti-pattern. The inefficient queries target 12 distinct anti-pattern types drawn from production workload studies. Each query is assigned to one of five tables with 6-7 queries per table.

## Results
The LLM analyzer classified 31 of 32 queries correctly. The aggregate results are:

- Accuracy: 96.9% (31/32) [95% CI: 83.8%, 99.9%]
- False positive rate: 0.0% (0/16) [95% CI: 0.0%, 20.6%]
- Recall: 93.8% (15/16) [95% CI: 69.8%, 99.8%]
- Result-equivalence rate: 93.3% (14/15) [95% CI: 68.1%, 99.8%]
- Total LLM cost: $0.005522

The single false negative was a UNION-based variant (score 35 < τ = 40), which is a minor anti-pattern appropriately scored below the detection threshold. All 16 baseline queries scored a consistent 15/100, and all flagged queries scored at least 40, demonstrating robust separation.

## Discussion
The pilot demonstrates that LLMs can serve as query-review assistants when embedded in an execution and validation harness. The framework does not assume the model is correct; it treats model output as a recommendation that must be stored, executed, and checked. This is important for big data environments where silent result drift can be more damaging than a slow query.

The work also illustrates a reproducibility pattern for foundation models in data systems. Rather than reporting only model responses, the artifact captures prompts, scores, token counts, cost, rewrites, execution outcomes, and validation status. The rule-based comparison clarifies the contribution: deterministic checks are enough for obvious patterns, while the LLM adds explanation and rewrite guidance when query structure is more context dependent.

## Limitations and Future Work
The experiment used 32 queries and 500-row tables. The 95% confidence interval for accuracy (83.8%–99.9%) is substantially narrower than the N=8 pilot (63.1%–100%), but still wider than a production-grade benchmark. A production-credible evaluation would require approximately 385 queries for ±5% margin. Until then, all performance claims must be interpreted as feasibility evidence for the architecture.

Future work should expand the query corpus beyond 100 queries, evaluate multiple LLMs (GPT-4o, Claude, Gemini, open-source models), test larger datasets (10K–1M rows), and study reviewer-facing explanations for big data governance under the 5V framework (volume, velocity, variety, veracity, value).

## Conclusion
This paper presented a reproducible framework for LLM-powered SQL query monitoring and optimization in big data environments. The framework integrates public dataset ingestion, controlled DuckDB workload execution, persistent SQLite query-history storage, structured LLM-based analysis with a defined prompt template, automated rewrite generation, execution-based tested-instance result validation through row-count and checksum comparison, and comprehensive cost accounting.

We evaluated the framework on a workload of 32 queries (16 baseline and 16 inefficient variants) across five datasets spanning scientific, environmental, cybersecurity, and commercial domains, targeting 12 anti-pattern types. The LLM analyzer achieved 96.9% detection accuracy (31/32), 0% false positive rate (0/16), and 93.8% recall (15/16). The single false negative—a UNION-based variant—is a minor anti-pattern appropriately scored below the detection threshold. Fourteen of fifteen rewrites preserved tested-instance result equivalence (93.3% result-equivalence rate). Total LLM API cost was $0.005522 for all 32 analyses, or approximately $0.000173 per query.

The results should be interpreted as evidence of feasibility, not as production-scale performance claims. The contribution is the framework itself: a modular, auditable artifact that can be extended, benchmarked, and compared against future approaches by the research community.

## References
\bibliographystyle{IEEEtran}
\bibliography{references}