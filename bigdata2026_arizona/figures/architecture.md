# Architecture Figure Draft

Use this as the basis for an IEEE-friendly vector figure.

```mermaid
flowchart LR
    A[DataSource\nmaintain_datasets.py] --> B[ExecutionEngine\nexecute_query_workload.py]
    B --> C[QueryHistoryStore\ncreate_db.py + schema]
    C --> D[LLMAnalyzer\nllm_analysis.py]
    D --> E[RecommendationEngine\ninside llm_analysis.py]
    C --> F[ReportGenerator\ngenerate_report.py + cost_analysis_report.py]
    E --> F
```

Suggested IEEE caption:

> Fig. 1. Framework architecture for reproducible LLM-powered query monitoring. Public datasets are prepared by DataSource, executed by ExecutionEngine, stored in QueryHistoryStore, analyzed by LLMAnalyzer, rewritten by RecommendationEngine, and summarized by ReportGenerator.

Submission note:

- IEEE prefers figures that remain legible in two-column format.
- Convert this diagram to PDF, EPS, or PNG before final submission if possible.
- Avoid relying on Mermaid rendering inside the final LaTeX paper.
