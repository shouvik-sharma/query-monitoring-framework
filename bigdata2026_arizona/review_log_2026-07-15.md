# Peer Review Log — 2026-07-15

**Paper:** LLM-Powered Query Monitoring and Optimization for Reproducible Big Data Workloads
**Author:** Shouvik Sharma, K. J. Somaiya College of Engineering
**Venue:** IEEE BigData 2026 Main Track
**Submission deadline:** August 21, 2026

---

## Review 1 — 10-Pass Editorial Audit

### Pass 1 — Compilation and Format

- PDF is 9 pages, within the 10-page IEEE limit. ✓
- IEEEtran.cls loaded correctly, single-blind author block present. ✓
- 9 Overfull hbox warnings remain:
  - Lines 163–163: 6.2pt (Table II — minor)
  - Lines 219–219: 28.5pt maximum overflow (Table III — significant; text protrudes into the margin in the rendered PDF column)
  - Lines 254–254: 1.2pt (Table IV — acceptable)
- All other Overfull boxes from the previous version are eliminated. Remaining are within acceptable range for IEEE two-column except the 28.5pt instance at line 219.

**Action required:** Add `\resizebox{\linewidth}{!}{...}` to Table III (Architectural Components) at line 202. It currently uses `\resizebox` on the outer table but the inner `p{...}` widths still sum wider than one column. Shrink the column widths: change `p{0.24\linewidth}p{0.34\linewidth}p{0.30\linewidth}` to `p{0.20\linewidth}p{0.38\linewidth}p{0.32\linewidth}` and re-compile.

### Pass 2 — Author Block and Affiliation

- LaTeX author block (line 22–24): `K. J. Somaiya College of Engineering`, India, `shouvik.s@somaiya.edu` — all consistent within the `.tex`. ✓
- **README.md line 33 still says: "Replace `Email: TODO` in the LaTeX author block before submission."** This is a stale instruction left from an earlier draft. The email is already in the `.tex`, so this is harmless to the PDF, but it is embarrassing if reviewers receive the source package and may signal sloppiness.
- `paper_ieee_bigdata2026.md` abstract still shows "Independent Researcher, India" — this conflicts with the `.tex` which says "K. J. Somaiya College of Engineering."

**Action required:** Update README.md line 33. Update `.md` file affiliation to match the `.tex`. Trivial, but must be done.

### Pass 3 — Citation Completeness

- Zero citations used in `.tex` that are missing from `references.bib`. ✓
- Zero undefined `\ref{}` targets. ✓
- 8 entries exist in `references.bib` but are never cited (`armbrust2021delta`, `bird2024bench`, `chen2021evaluating`, `duckdbdocs`, `graefe1993volcano`, `kraska2018case`, `li2023llmsql`, `zaharia2016apache`). These are leftover from earlier drafts. They do not appear in the rendered bibliography and are harmless, but they bloat the `.bib` file. Clean up before camera-ready.
- `huo2025bird` (BIRD-INTERACT): correctly has `note = {arXiv preprint}` with no fake ID. ✓
- `keebo2023`: Still formatted as `@misc` with `howpublished = {Proc. ACM SIGMOD}`. This renders awkwardly in the bibliography ("Proc. ACM SIGMOD, 2023" with no venue details). Change to `@inproceedings` before camera-ready. Not blocking.

### Pass 4 — Cross-Reference Integrity

- **FAIL — 3 figures defined but never referenced in the text body.**
- Labels defined: `fig:architecture`, `fig:detection`, `fig:validation`, `fig:cost`. References in text body via `\ref{fig:...}`: only `fig:architecture`. This means Figures 2, 3, and 4 are never pointed to in the prose. In IEEE papers, every figure must be explicitly referenced ("as shown in Fig. 2", "see Fig. 3 left"). Figures 2, 3, and 4 currently float without any in-text citation.

**Action required (BLOCKING):** Add `\ref{}` callouts in the prose:

- After the threshold sensitivity paragraph (line ~402): add "Figure~\ref{fig:detection} (left) shows the per-query scores; the right panel confirms clean separation of the two classes."
- Before or after the result-equivalence rate equation (line ~469): add "Figure~\ref{fig:validation} (left) summarizes validation outcomes per anti-pattern; the right panel shows runtime comparison at sub-millisecond scale."
- After the per-query cost paragraph (line ~507): add "Figure~\ref{fig:cost} shows the near-uniform per-query API cost distribution."

### Pass 5 — Internal Number Consistency

- **PARTIAL FAIL — one inconsistency found.**
- All numbers in abstract, Table VII, equations (10), and conclusion are consistent: 96.9%, 0%, 93.8%, 93.3%, $0.005522. ✓
- **Table VII and the text disagree on the score margin:**
  - Table VII, row "Score margin": `20--25 pts`
  - Text at line 392: "The minimum margin between the highest baseline score (15) and the lowest flagged score (40) was **25 points**"
  - Table VIII row "Score margin": `25 pts` for N=32
- The correct value is 25 points (15 to 40). The "20--25 pts" range in Table VII is unexplained and inconsistent. Either the range should be explained (if it represents min/max across some variation) or the cell should read `25 pts` to match the text.

**Action required:** Change Table VII "Score margin" from `20--25 pts` to `25 pts`, or add a footnote explaining what the range represents.

### Pass 6 — Internal Logic Contradiction (BLOCKING)

- **FAIL — Section 3.3 directly contradicts the experimental setup.**
- Line 149: *"The framework targets the **four most prevalent** SQL anti-patterns reported in production big data workloads."* Table II then lists exactly four patterns.
- But the workload (Table VI) and the abstract both state **12 distinct anti-pattern types**. Section 5.2 workload design and the conclusion confirm 12 types are tested.
- This is a direct contradiction within the same paper. A reviewer reading Section 3.3 will see "four" and then see "12" in Section 5.2 and correctly flag this as a fundamental inconsistency. It suggests the design section was written when the workload had only 4 types and was never updated when it expanded to 12.

**Action required (BLOCKING):** Rewrite Section 3.3 (lines 148–168) to acknowledge all 12 anti-pattern types in the workload, not just the four shown in Table II.

**Option A (recommended):** Keep Table II as a "core four" summary for the formalism, but update the surrounding text: *"The framework's taxonomy begins with the four anti-patterns most commonly reported in production big data studies [6],[15], and extends to 12 types in the experimental workload (Section~\ref{sec:workload})."*

**Option B:** Expand Table II to show all 12 anti-patterns with formal notation, but this may exceed the page budget.

### Pass 7 — Algorithm Correctness

- **FAIL — Algorithm 1 has a logic error.**
- Algorithm 1 (lines 176–196) declares `R ← ∅` at the start and returns `R, C` at the end, but `R` is never updated inside the loop. Detection outcomes (whether a query was flagged) are written to the database via `store_comparison()` but are never accumulated into `R`. The returned `R` is always the empty set.
- This is not catastrophic — the framework obviously works because results are persisted to the database, not returned in memory — but a reviewer who reads the pseudocode carefully will flag this as a logical error. The algorithm says it returns a detection report `R` but provably never populates it.

**Action required:** Either (a) add `R ← R ∪ {(q_i, s_i ≥ τ)}` inside the loop before `ENDFOR`, or (b) remove `R` from the return value and change the output description to "Detection and cost records are persisted to QueryHistoryStore; C accumulates comparison metadata." Option (b) is more honest to the actual implementation.

### Pass 8 — Broken Prose in Section 3.2 (BLOCKING)

- **FAIL — Dangling sentence fragment between two equations.**
- Lines 144–146 read:

  > "...We report runtime improvement and LLM cost as separate quantities rather than combining milliseconds and dollars into a single scalar benefit. **Detection metrics are:**
  >
  > **The standard formulas are:** $TP$ = inefficient queries scored ≥ τ..."

- The sentence "Detection metrics are:" ends without completing, and the next sentence starts with "The standard formulas are:" which is a second incomplete lead-in. These two half-sentences are left from a previous version where a `\begin{equation}` block sat between them. The equations were removed or moved but the broken prose was not cleaned up.

**Action required (BLOCKING):** Replace lines 144–146 with a single clean sentence:

```latex
where $p_{\text{in}} = \$0.15/10^6$ tokens and
$p_{\text{out}} = \$0.60/10^6$ tokens (GPT-4o-mini)~\cite{openai2026models}.
We report runtime and cost as separate quantities.
Standard detection metrics are: $TP$ = inefficient queries scored $\geq \tau$;
$TN$ = baselines scored $< \tau$; $FP$ = baselines incorrectly flagged;
$FN$ = inefficient queries missed.
```

### Pass 9 — `.md` File Staleness

- **FAIL — `paper_ieee_bigdata2026.md` contains the obsolete N=8 version.**
- The `.md` file uploaded as part of this package still contains the old abstract with:
  - "three public datasets and **eight** queries"
  - "100% detection accuracy"
  - "75% semantic-match rate"
  - "$0.000671" total cost
  - "3-row pilot tables"
  - "Independent Researcher, India" affiliation
- All of these contradict the `.tex`. While the `.md` is not the submission artifact (the PDF is), this file is in the same repository folder. If reviewers receive a source package, or if it is committed to the GitHub repository, it will create confusion about which version of the paper is the canonical submission and could raise questions about the integrity of reported results.

**Action required:** Either delete `paper_ieee_bigdata2026.md` or update its entire content to match the current `.tex` precisely.

### Pass 10 — Reviewer-Perspective Assessment Against Historical IEEE BigData Papers

- **CONDITIONAL — Borderline for main track; suitable for Special Session.**

| Criterion | Score | Commentary |
|-----------|-------|------------|
| Novelty of contribution | 3/5 | End-to-end governance pipeline is genuinely new; but the LLM used is off-the-shelf GPT-4o-mini and no model innovation is present |
| Experimental scale | 2/5 | N=32 queries, 500 rows — honest but weak by main-track standards |
| Related work coverage | 4/5 | Five distinct theme areas, gap statement is clear |
| Writing quality | 2.5/5 | Good structure, but broken prose (Pass 8) and unreferenced figures (Pass 4) significantly hurt |
| Reproducibility | 5/5 | `reproduce.py`, public GitHub, public datasets, seeded RNG, temperature=0 — exemplary |
| Technical rigor | 3.5/5 | 95% CIs, sample-size calculation, honest limitations — well above average |
| Big Data relevance | 3.5/5 | Explicitly addresses variety (5 domains), governance, and 5Vs — solid fit |

---

## Review 2 — BigData CFP Positioning Review (jh)

### Topic and Venue Fit

- Your paper targets LLM-powered query monitoring and SQL optimization for big-data workloads, with an explicit focus on infrastructure, governance, and reproducible benchmarking.
- BigData 2026 calls out data mining, databases, AI/ML, scalable systems, and big-data platforms, plus interest in foundation models and LLMs in associated events and workshops, so your topic is squarely within scope.
- The submission checklist correctly maps the work to "Big Data Infrastructure," "Big Data Management," "Big Data Benchmarks," and "Foundation Models for Big Data," which is a strong alignment.

### Positioning vs Historical Accepted Work

- Recent accepted papers in related IEEE big-data venues include LLM-based systems such as RAG-style chatbots, LLMs for robotic task execution, and LLM-powered biomedical relation extraction.
- Compared to these, your work is less about an application domain and more about infrastructure: an auditable framework for LLM-assisted query governance, which is under-represented and could stand out if framed clearly as systems/benchmark work.
- BigData's competitive acceptance rate (≈17–18%) means infrastructure papers must demonstrate both conceptual novelty and convincing empirical support; you're halfway there with the framework and metrics, but scale and comparative baselines need sharpening.

### Novelty and Contribution Clarity

- The abstract and introduction clearly state four contributions: modular architecture, reproducible artifact, pilot benchmark, and explicit limitations.
- Novelty is mainly in combining static anti-pattern detection, LLM semantic analysis, and execution-based validation in one pipeline with cost accounting, which is distinct from optimizer-hint or plan-search papers cited in your related work.
- To match historical BigData research papers, you should sharpen the "what's new" message in one short paragraph that contrasts your end-to-end monitoring pipeline with prior LLM-for-optimization work (R-Bot, LLMOpt, LLMSTEER, etc.).

### Experimental Design and Metrics

- The evaluation uses 5 logical datasets (USGS earthquakes, NOAA weather, AWID intrusion, UCI-derived products, UCI-derived orders), each with 500 rows, and a workload of 32 queries split into 16 baseline and 16 intentionally inefficient variants across 12 anti-pattern types.
- You compute standard classification metrics (accuracy, false positive rate, recall) for detection, plus result-equivalence metrics (row-count and SHA-256 checksum match) and detailed LLM API cost accounting.
- This metric set is good and in line with rigorous systems papers, but you'd benefit from at least one additional perspective—e.g., breakdown of detection/recall per anti-pattern type or per dataset domain—which reviewers often expect to understand generality.

### Scale and Claim Calibration

- You explicitly state that the workload is a pilot feasibility study on 500-row tables, not a production performance benchmark, and emphasize that the contribution is the architecture and artifact rather than raw performance numbers.
- Historical BigData papers typically show either large-scale data (millions of records) or strong domain complexity; your current artifact is small but nicely controlled, so it may be perceived as "toy scale" unless you clearly justify why this scale is sufficient for the monitoring/semantics question.
- The checklist already flags "Consider adding larger-scale experiments before Aug. 21, 2026," which is exactly what would move the paper closer to the empirical expectations of BigData.

### Reproducibility and Artifact Quality

- The framework is open source with scripts for dataset preparation, workload execution, query history storage, LLM analysis, and report generation, plus a mermaid architecture diagram.
- You provide details of hardware, DuckDB version, SQLite usage, LLM configuration (GPT-4o-mini, temperature 0, max tokens 1024), and seeded randomness for synthetic datasets, which aligns with modern artifact-friendly systems practices.
- Relative to historical BigData infrastructure papers, this artifact story is competitive; the main improvement would be a finalized architecture figure in IEEE-friendly vector format and a short "artifact note" section summarizing how to reproduce the main tables and metrics.

### Related Work Coverage

- Your related work section references static SQL analysis tools, LLM-based query rewriting and optimization, cloud warehouse monitoring, and classical benchmarks.
- This breadth is strong and shows you are anchored in current LLM-for-databases literature, which BigData reviewers will appreciate.
- What's missing is a short paragraph explicitly situating your work relative to BigData's own ecosystem.

### Writing and Structure

- The manuscript uses IEEEtran conference format, has a clear abstract, introduction, related work, system architecture, experimental setup, evaluation, limitations, and conclusion.
- The technical prose is generally concise and readable, and you already include an explicit "limitations and future work" discussion, which matches expectations for serious systems papers.
- A few areas could be tightened: move some low-level implementation details from the main text into an appendix or artifact note to free space for deeper analysis, and make sure all tables are clearly referenced and discussed in the narrative rather than only presented.

### Format and Submission Compliance

- You are using the IEEE Computer Society proceedings format and IEEEtran.cls, with two-column layout and proper packages.
- The submission checklist notes several remaining tasks: confirm the paper is ≤10 pages including references, ensure all figures/tables are numbered and cited, verify references render in numeric IEEE style, and finalize email/affiliation consistency.

### Track Selection and Strategic Positioning

- Your work is best positioned in the main research track or a special session that explicitly mentions LLMs and data mining, provided you emphasize the big-data governance and foundation-model-assisted analytics angle rather than only query optimization.
- If you are concerned about scale, an Industrial/Government or domain-focused session that values practical frameworks and reproducible artifacts may be a good secondary option.

### Priority Recommendations

1. Add at least one larger-scale experiment.
2. Deepen the analysis of detection behavior.
3. Sharpen the novelty claim and BigData alignment.
4. Consider mentioning that your artifact could serve as a starting benchmark.
5. Finalize the architecture figure and artifact note.
6. Clean up formatting and checklist items.

---

## Review 3 — 10-Iteration Systematic Audit

### Iteration 1: Track Alignment & Scope Validation

- Your draft targets Big Data Infrastructure, Big Data Management, Big Data Benchmarks, and Foundation Models for Big Data.
- Historical Fit: IEEE BigData papers in Infrastructure and Management demand distributed architectures and extreme scale. Your architecture is built on DuckDB (embedded) and SQLite (single-node).
- Verdict: Your work fits best under the Foundation Models for Big Data track (focusing on LLM orchestration) or the Big Data Benchmarks track (as an evaluation harness). It is highly unlikely to be competitive in the pure systems/infrastructure tracks.

### Iteration 2: The Scale of Evaluation (The "Big Data" Paradox)

- Your pilot draft evaluated on 3-row tables; your expanded draft uses 500-row tables.
- Historical Fit: Reviewers at IEEE Big Data will strongly object to calling an evaluation on 500 rows "Big Data." At this scale, query runtimes are in micro- or low milliseconds, making performance deltas completely dominated by system noise.
- Verdict: A 500-row evaluation is a major vulnerability for a Full Research Paper.

### Iteration 3: Major Internal Discrepancy & Text Desynchronization

- The package contains two conflicting versions of your text:
  - Source 4 (Pilot Draft): 3 datasets, 8 queries, 3-row tables, $0.000671 cost.
  - Source 6 (Expanded Draft): 5 datasets, 32 queries, 500-row tables, $0.005522 cost.
- Historical Fit: Blatant internal contradictions in a paper signal low quality control and result in a swift, unanimous rejection.
- Verdict: You must meticulously scrub your draft to ensure 100% consistency.

### Iteration 4: Baseline & SOTA Competitive Comparisons

- You compare your LLM-based approach conceptually to rule-based tools in Table I. However, you do not perform an actual empirical comparison by running existing open-source static analyzers on your query workload.
- Historical Fit: IEEE Big Data research papers must demonstrate how a new approach outperforms or uniquely complements state-of-the-art baselines.
- Verdict: To defend your high accuracy (96.9%), you must run at least one of these open-source tools on your 32-query workload and report a side-by-side performance comparison.

### Iteration 5: Equivalence & Semantic Validation Rigor

- Your framework relies on comparing sorted row counts and SHA-256 result checksums to validate if a rewritten query preserves the original query's semantics.
- Historical Fit: Database researchers will point out that row count and sorted checksum equivalence on small (500-row) datasets is a necessary but insufficient condition to guarantee semantic equivalence.
- Verdict: You must include a robust "Discussion" section addressing this limitation.

### Iteration 6: LaTeX Overfull \hbox Layout Bleed

- The pdfTeX log shows several layout-breaking errors with Overfull \hbox warnings up to 28.50977pt too wide.
- Historical Fit: Overfull boxes mean text is bleeding out of the columns and into the margins, which looks highly unprofessional and violates IEEE camera-ready guidelines.
- Verdict: You must fix these. Avoid using long, unbreakable typewriter-font text in standard columns.

### Iteration 7: BibTeX & Bibliography Sanity Check

- The compilation uses 25 entries with IEEEtran.bst. The references are exceptionally timely.
- Historical Fit: IEEE Big Data reviewers appreciate highly current and complete literature reviews.
- Verdict: The bibliography is in excellent shape. However, verify if preprints have since been formally published and update their citations accordingly.

### Iteration 8: Affiliation Consistency

- In the pilot draft, you list yourself as an Independent Researcher, while the expanded draft lists K. J. Somaiya College of Engineering.
- Historical Fit: Academic and institutional affiliations provide immediate perceived credibility to reviewers.
- Verdict: Use your academic institutional affiliation consistently across the submission.

### Iteration 9: Technical Novelty vs. Engineering Depth

- Your paper spans 9 pages. Yet, the core technical contribution is an orchestration pipeline (connecting DuckDB, SQLite, and OpenAI API).
- Historical Fit: Full papers at IEEE Big Data are expected to present novel algorithms, deep theoretical insights, or major empirical breakthroughs. A paper that is purely a "wrapper pipeline" evaluated on a small dataset will be criticized for lack of novelty.
- Verdict: Since the pipeline is highly practical and fully open-sourced, its nature aligns more with a systems tool than a theoretical breakthrough.

### Iteration 10: Overall Submission Competitiveness & Strategic Options

- Your paper in its current form (9 pages, 500-row tables) stands a high chance of being rejected in the Full Research Paper track due to scale limitations.
- Verdict: You have three distinct strategies:
  - **Option A (The Scale-Up):** Keep it as a Full Paper, but immediately scale up the evaluation to standard benchmark scales (e.g., TPC-H at Scale Factor 1 or 10, meaning millions of rows).
  - **Option B (The Demo Track):** Condense the paper to 4 pages and submit to the IEEE BigData 2026 Demo Track (which explicitly welcomes fully implemented systems and artifact links). This is your highest-probability path to acceptance.
  - **Option C (Workshop Track):** Submit to a specialized workshop co-located with the conference, where pilot studies are highly welcomed.

---

## Review 4 — Editorial Reject-Encourage-Resubmit

### Overall Verdict

- Reject in its current form; encourage resubmission after major revision.
- The subject is relevant to IEEE BigData 2026, and the framework has the beginnings of a useful systems contribution. However, the current package falls below the historical bar for a regular paper because its principal claims rest on 32 author-designed queries, five 500-row datasets, one model, one inference run, one execution engine, and no experimental baseline. Several technical statements are also incorrect, and—most seriously—the public artifact does not currently reproduce the experiment reported in the PDF.

### Pass 1 — Venue Relevance: Pass

- The paper fits several topics explicitly listed in the call: Big Data Infrastructure and Management, Big Data Governance, Foundation Model operationalization, Big Data benchmarking and evaluation frameworks.
- The risk is that the paper repeatedly invokes "big data workloads" while evaluating tables with only 500 rows. The work currently demonstrates query-governance workflow feasibility, not big-data performance.
- The framing should emphasize auditable SQL review, recommendation provenance, rewrite safety, and governance rather than query optimization at big-data scale.

### Pass 2 — Compliance: Weak pass

- The PDF is nine pages and fits the ten-page full-paper limit. It uses the IEEE two-column format and contains author identity (single-blind).
- However, the package is not submission-ready: README still says to replace Email: TODO; checklist still marks "compile final PDF" and "confirm final paper is ≤10 pages" as unfinished; PDF identifies author with K. J. Somaiya College of Engineering, while Markdown source says "Independent Researcher."
- The affiliation must be accurate and institutionally authorized.

### Pass 3 — Research questions: Weak

- The manuscript describes a pipeline, but it does not formulate clear, falsifiable research questions. As a result, the evaluation appears to demonstrate that the software runs rather than testing a scientific hypothesis.
- Use explicit questions such as:
  - RQ1: How accurately does LLM-assisted review detect SQL risks compared with deterministic static-analysis baselines?
  - RQ2: How often do generated rewrites execute successfully and preserve results across multiple database instances?
  - RQ3: What are the latency, monetary cost, and stability tradeoffs among rule-based, LLM-only, and hybrid approaches?
  - RQ4: How does performance change across models, engines, schemas, and anti-pattern categories?

### Pass 4 — Originality: Fail

- The current contribution is primarily an orchestration of DuckDB query execution, SQLite telemetry storage, LLM prompting, SQL rewrite generation, row-count and checksum comparison, and cost reporting.
- That is useful engineering, but each component is conventional. The manuscript must demonstrate that their combination produces a result that existing static analyzers and LLM optimization systems do not already provide.
- Your strongest possible novelty is not "LLMs can detect SQL anti-patterns." It is: a persistence-first, auditable governance framework that combines deterministic detection, LLM explanations and rewrites, execution validation, provenance, and cost accounting.
- To support that claim, the paper needs a hybrid baseline and ablation study.

### Pass 5 — Related work and references: Fail

- **Broken or weak source integrity:** The cited querylens/querylens repository currently returns a 404. This reference should not remain in a submission unless the correct permanent source is found. The cited sqlaudit project exists and implements rules covering many of your tested categories.
- **Unsupported novelty language:** Statements such as "None provides an end-to-end monitoring pipeline…" are too absolute without a systematic literature review. Use defensible language: "Among the systems examined in our review, we did not identify one that jointly persists query telemetry, records structured LLM recommendations, validates generated rewrites through re-execution, and reports per-query model cost."
- Include a comparative table with columns such as: System, Static detection, LLM rewrite, Execution telemetry, Rewrite validation, Persistent provenance, Public artifact.

### Pass 6 — Experimental methodology: Fail

- The current study contains: 32 queries, 16 manually designed baseline queries, 16 manually altered inefficient variants, five schemas with 500 rows each, one model, one model configuration, one execution engine, author-provided ground truth, no independent test set, no baseline system.
- This design is vulnerable to confirmation bias. The evaluator knows the anti-pattern taxonomy, creates the queries, defines the expected labels, writes the prompt, chooses the threshold, and interprets the model output.
- The paper therefore measures performance on a purposively constructed demonstration set, not general detection ability.
- **Minimum acceptable experimental expansion:**
  - At least 100–200 queries.
  - A held-out test set not used while designing the prompt.
  - TPC-H, TPC-DS, JOB, or another established workload.
  - Hard negative queries that superficially resemble anti-patterns but are valid.
  - Queries with multiple simultaneous issues.
  - Deterministic AST/rule baseline.
  - At least one established SQL-analysis tool.
  - One hybrid system: rules first, LLM only for contextual cases.
  - Multiple LLM calls per query.
  - Preferably two SQL engines.

### Pass 7 — Technical correctness: Fail

- **Threshold analysis is mathematically wrong:** The manuscript says a positive query scored 40 and uses the rule s_i ≥ τ. It then says accuracy remains 31/32 for 40<τ≤50. That cannot be true. Once τ>40, the query scored exactly 40 becomes an additional false negative. Regenerate the complete threshold table and ROC or precision–recall analysis programmatically.
- **Temperature zero does not ensure full reproducibility:** The manuscript says "Temperature t=0 eliminates model stochasticity, making all results fully reproducible." This is too strong. Temperature zero reduces sampling variability but does not guarantee identical hosted-model responses across repeated calls, backend changes, or provider revisions. Use: "Temperature t=0 reduces sampling variability; exact output reproducibility is not guaranteed for a hosted model." Then perform repeated runs and report observed stability.
- **Validation logic is phrased incorrectly:** The paper states "If neither the row count nor the checksum matches…" The intended rule requires both to match. Therefore: "If either the row count or checksum differs, the rewrite is marked as a tested-instance result mismatch."
- **Idempotence is overstated:** The paper claims every pipeline stage is idempotent. An external LLM call is not necessarily idempotent unless responses are cached and replayed by a stable request identifier. State exactly which stages are idempotent and which are replayable only through stored outputs.

### Pass 8 — Evaluation validity: Fail

- **"Result equivalence" remains too permissive:** The revised term "tested-instance result-equivalence" is better, but several counted successes are not safe optimizations: Adding LIMIT changes the result contract; Removing the leading % from LIKE '%term' changes matching behavior; Adding a filter changes query intent; Replacing a cross join with an inner join assumes a relationship not expressed by the original query; Replacing SELECT * with selected columns changes the output schema.
- Classify recommendations into: Semantics-preserving rewrite, Correctness repair, Intent-dependent recommendation, Performance suggestion requiring user approval, Unsafe or rejected rewrite. Only category 1 should count toward an automatic rewrite-equivalence metric.
- **Runtime results do not support optimization claims:** The manuscript acknowledges that runtimes are sub-millisecond and dominated by measurement noise.

### Pass 9 — Artifact reproducibility: Critical fail

- The public artifact does not currently reproduce the experiment reported in the PDF.

### Pass 10 — Writing, figures, and presentation: Weak pass

---

## Synthesis — Cross-Review Issue Table

| Issue | Review 1 (10-Pass) | Review 2 (jh) | Review 3 (Systematic Audit) | Review 4 (Editorial) |
|-------|:-:|:-:|:-:|:-:|
| Scale too small (500 rows, 32 queries) | Cond. | ✓ | ✓ | ✓ |
| Missing rule-based baseline | — | ✓ | ✓ | ✓ |
| Stale `.md` / internal inconsistencies | B3, S3 | — | ✓ | ✓ |
| Broken prose (detection metrics, lines 144–146) | B2 | — | — | — |
| Unreferenced figures (2,3,4) | B1 | — | — | — |
| Section 3.3: "four" vs "12" anti-patterns | B3 | — | — | ✓ |
| Algorithm 1: `R` never populated | B4 | — | — | — |
| Score margin inconsistency (20–25 vs 25) | S1 | — | — | — |
| Overfull hbox (Table III, 28.5pt) | S2 | — | ✓ | ✓ |
| Threshold analysis mathematically wrong | — | — | — | ✓ |
| Temperature-0 reproducibility overclaimed | — | — | — | ✓ |
| Validation logic wording ("neither/nor") | — | — | — | ✓ |
| Rewrite safety (LIMIT, LIKE, SELECT *, etc.) | — | ✓ | ✓ | ✓ |
| No explicit research questions | — | — | — | ✓ |
| Confirmation bias (author-designed queries) | — | — | — | ✓ |
| Keebo `@misc` vs `@inproceedings` | M1 | — | — | — |
| Idempotence overclaimed | — | — | — | ✓ |
| Artifact doesn't reproduce paper | — | — | — | ✓ |
| Demo Track as alternative | ✓ | ✓ | ✓ | — |

---

## Prioritized Action Plan

### Tier 1: Blocking (must fix before any submission)

| # | Item | Time |
|---|------|------|
| B1 | Add `\ref{fig:detection}`, `\ref{fig:validation}`, `\ref{fig:cost}` callouts | 15 min |
| B2 | Replace dangling "Detection metrics are:" fragment (lines 144–146) | 2 min |
| B3 | Rewrite Section 3.3: "four" → acknowledge 12 anti-patterns | 5 min |
| B4 | Fix Algorithm 1: add `R ← R ∪ {(q_i, s_i ≥ τ)}` or remove `R` from returns | 2 min |
| B5 | Threshold analysis: recompute confusion matrix for all τ values | 30 min |
| B6 | Temperature-0 claim: soften to "reduces sampling variability" | 2 min |
| B7 | Validation wording: "neither row count nor checksum" → "either row count or checksum" | 2 min |
| B8 | Score margin: Table VII "20–25 pts" → "25 pts" | 2 min |
| B9 | Overfull hbox Table III: adjust column widths to `p{0.20\linewidth}p{0.38\linewidth}p{0.32\linewidth}` | 5 min |
| B10 | Delete/update `paper_ieee_bigdata2026.md` | 5 min |
| B11 | Update README: remove "Replace Email: TODO" | 2 min |
| B12 | Affiliation consistency: ensure `.md`, README, `.tex` all match | 5 min |
| B13 | Keebo citation: change `@misc` to `@inproceedings` | 2 min |

### Tier 2: Significant (adds credibility, do before any submission)

| # | Item | Time |
|---|------|------|
| S1 | Rewrite safety classification: categorize rewrites into semantics-preserving / correctness repair / intent-dependent / unsafe; only count category 1 as automatic equivalence | 2 hours |
| S2 | Add explicit research questions (RQ1–RQ4) framing evaluation | 1 hour |
| S3 | Idempotence qualification: specify which stages are truly idempotent | 15 min |
| S4 | Novelty positioning paragraph in introduction | 1 hour |
| S5 | Remove querylens 404 reference | 10 min |
| S6 | Qualify "None provides an end-to-end monitoring pipeline" language | 10 min |

### Tier 3: Experimental additions (for Special Session / Sep 30)

| # | Item | Time |
|---|------|------|
| E1 | Rule-based baseline: run `sqlaudit` or `bigquery-antipattern-recognition` on 32-query workload; report P/R/F1 side-by-side | 1 week |
| E2 | Scale extension: extend one or two datasets to ≥100K rows; show pipeline still works | 1 week |
| E3 | Per-pattern / per-dataset breakdown | 3 days |
| E4 | Held-out test set: set aside 20% of queries for final evaluation | 3 days |
| E5 | Multiple LLM calls per query (3–5 runs); report variance | 2 days |
| E6 | Confidence interval clarification: add note that binomial CIs assume random sampling | 15 min |
| E7 | Clarify runtime claims: acknowledge sub-ms differences are noise-dominated | 15 min |

### Tier 4: Cleanup (camera-ready)

| # | Item | Time |
|---|------|------|
| C1 | Remove 8 unused bib entries | 10 min |
| C2 | Final LaTeX pass for remaining overfull boxes | 30 min |
| C3 | Verify artifact reproducibility: run `reproduce.py` end-to-end | 1 hour |

---

## Strategic Recommendation

### Two-Track Submission Strategy

**Track A – Demo Track submission (Aug 21)**
- 4-page paper, no scale-up needed
- `reproduce.py` is the star
- Highest probability path with current data

**Track B – Full paper for Special Session (Sep 30)**
- Address all blocking + significant issues
- Add rule-based baseline
- Scale up
- Submit to *Special Session on Machine Learning on Big Data*

If attempting main track on Aug 21, fix all Tier 1 items (~2 hours) + Tier 2 items (~4 hours).

### Estimated Timeline

| Phase | Deadline | Effort |
|-------|----------|--------|
| Fix Tier 1 (13 items) | Aug 14 | ~2 hours |
| Submit Demo Track (4-page) | Aug 21 | ~4 hours (condense + format) |
| Submit main track (if attempting) | Aug 21 | Already fixed |
| Tier 2 + Tier 3 additions | Sep 15 | ~2–3 weeks |
| Submit Special Session | Sep 30 | ~1 more week polish |

---

*Review log compiled 2026-07-15. Based on four independent editorial reviews of the complete LaTeX source, compiled log, BibTeX database, and supporting files.*
