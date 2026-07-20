# Required LaTeX & Layout Fixes - BigData 2026 Submission

## Summary
This document outlines the critical LaTeX and layout corrections needed to make the IEEE BigData 2026 submission package ready for camera-ready review. Each fix is documented with the specific issue, proposed solution, and exact LaTeX code changes required.

## Algorithm Pseudocode Correction

### Problem
Algorithm~\ref{alg:pipeline} declares `R ← ∅` at the start and returns `R, C` at the end, but `R` is never updated inside the loop. Detection outcomes are written to the database via `store_comparison()` but never accumulated into `R`.

### Fix
Removed `R` from the algorithm. It was being declared but never updated; detection outcomes are directly persisted to QueryHistoryStore, so the empty `R` variable was misleading.

#### Implementation (fixed algorithm):

**Fixed algorithm (lines 180-196):**
```latex
\begin{algorithm}[t]
\caption{LLM-Powered Query Monitoring Pipeline}
\label{alg:pipeline}
\begin{algorithmic}
\STATE \textbf{Input:} Dataset list $D$, workload $Q$, engine $E$, threshold $\tau$
\STATE $C \gets \emptyset$
\FOR{each $(q_i, d_i) \in (Q, D)$}
  \STATE $M_i \gets \text{exec}(q_i, d_i, E)$ \hfill $\triangleright$ Execute original
  \STATE $\text{store\_query}(q_i)$
  \STATE $\text{store\_execution}(q_i, M_i, \text{label}=\text{original})$
  \STATE $(s_i, I_i, q'_i) \gets \text{LLM\_analyze}(q_i)$
  \STATE $\text{store\_llm\_analysis}(q_i, s_i, I_i)$
  \IF{$s_i \geq \tau$}
    \STATE $M'_i \gets \text{exec}(q'_i, d_i, E)$
    \STATE $\text{store\_execution}(q'_i, M'_i, \text{label}=\text{rewritten})$
    \STATE $\textit{resEq}_i \gets \text{resEq}(q_i, q'_i)$
    \STATE $\Delta_i \gets \text{cost\_delta}(M_i, M'_i)$
    \STATE $c_i \gets \text{llm\_cost}(\text{tok}_{\text{in}}, \text{tok}_{\text{out}})$
    \STATE $\text{store\_recommendation}(q_i, q'_i)$
    \STATE $\text{store\_comparison}(q_i, \textit{resEq}_i, \Delta_i, c_i)$
  \ENDIF
\ENDFOR
\RETURN $C$\textemdash detection outcomes and comparison records are persisted to QueryHistoryStore.
\end{algorithmic}
\end{algorithm}
```

## Formatting Fixes

### Problem
- Dangling sentence fragment "Detection metrics are:" between equations (lines 144-146)
- Missing explicit research questions for evaluation clarity

### Fix
Clean up prose and add clear research questions RQ1-RQ4.

#### Implementation (cleanup prose - recommended replacement for lines 144-146):
```latex
where $p_{\text{in}} = \$0.15/10^6$ tokens and
$p_{\text{out}} = \$0.60/10^6$ tokens (GPT-4o-mini)~\cite{openai2026models}.
We report runtime and cost as separate quantities.
Standard detection metrics are: $TP$ = inefficient queries scored $\geq \tau$;
$TN$ = baselines scored $< \tau$; $FP$ = baselines incorrectly flagged;
$FN$ = inefficient queries missed.
```

#### Implementation (explicit research questions - recommended replacement in current Abstract): 
```latex
We evaluate the framework on a workload of 32 queries (16 baseline and 16 inefficient variants) across five datasets spanning scientific, environmental, cybersecurity, and commercial domains, targeting 12 anti-pattern types. The LLM analyzer achieves 96.9\% detection accuracy (31/32), 0\% false positive rate (0/16), and 93.8\% recall (15/16). The single false negative---a UNION-based variant---is a minor anti-pattern appropriately scored below the detection threshold. Fourteen of fifteen rewrites preserved tested-instance result equivalence (93.3\% result-equivalence rate). Total LLM API cost was \$0.005522 for all 32 analyses, or approximately \$0.000173 per query.

This work addresses four research questions: \textbf{RQ1:} How accurately does LLM-assisted review detect SQL anti-patterns on a labeled pilot workload? \textbf{RQ2:} How often do generated rewrites execute successfully and preserve results? \textbf{RQ3:} What latency and monetary-cost overheads are introduced by LLM-assisted monitoring? \textbf{RQ4:} How does performance vary across datasets and anti-pattern categories?
```

## Additional Formatting Improvements

### Problem
- Score margin inconsistency (Table VII shows "20--25 pts" vs text says "25 points")
- Overfull hbox warnings in PDF (Table III - 28.5pt overflow)
- Stale README.md and paper_ieee_bigdata2026.md files
- Keebo citation format (@misc instead of @inproceedings)

### Fixes
See Tier 1 action plan in review_log_2026-07-15.md for specific line numbers and code changes.