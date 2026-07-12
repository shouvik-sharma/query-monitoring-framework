# Preparation Guide for Publication

## 1. Proofreading & Formatting
- **Grammar & Style**: Run `pandoc --from=markdown --to=markdown --output=checked.md RESEARCH_PAPER.md` or use a linter like `markdownlint`. Fix any typos, maintain consistent tense.
- **Reference Style**: Convert the current generic citations (e.g. numbered) to the style required by the target venue (IEEE, ACM, etc.). Use a citation manager (Zotero, JabRef) and export to BibTeX.
- **Figure & Table Captions**: Ensure all captions are self‑contained and refer to the correct figure/table number.

## 2. Reproducibility Checklist
- **Data**: Place the 3‑row pilot CSVs in `data/raw/`. Include a `data/dataset_manifest.json` listing URL, size, and checksum.
- **Scripts**: Verify `scripts/create_query_workload.py`, `scripts/execute_query_workload.py`, `scripts/llm_analysis.py`, and `scripts/generate_report.py` run end‑to‑end without manual intervention.
- **Environment**: Create a `requirements.txt` and optionally a `conda.yml` file. Optionally build a Docker image (see `Dockerfile` if present).
- **License**: MIT license for code; dataset licensing is covered by original sources.
- **DOI & Code Hosting**: Publish the repo on GitHub and acquire a DOI via Zenodo (GitHub → Zenodo integration). Include the DOI in the paper.

## 3. Ethical & Data‑Availability Statements
- Add a **Data Availability** section describing that all datasets are public and the aggregated 3‑row samples are included.
- Add an **Ethics** section stating no personal data was used and that public data usage is compliant with license terms.

## 4. Target Venue & Formatting
- **Choose venue**: e.g., *VLDB 2026*, *SIGMOD 2026*, or *IEEE Big Data*.
- Download the style files (e.g., `.bst`, `.cls`) and run `pdflatex` to check for errors.
- Convert the markdown to LaTeX using `pandoc -f markdown -t latex -o paper.tex RESEARCH_PAPER.md` and edit the resulting `.tex` to satisfy formatting requirements.

## 5. Supplementary Material
- A `.zip` of the `data/`, `scripts/`, and a `README` explaining how to reproduce results.
- An explicit ``Results`` folder containing `query_history.db` with the measured results.

## 6. Communication & Submission
- Draft a cover letter: summarize novelty, reproducibility, and contact details.
- Include an ACM/IEEE *Author Contribution* table.
- Submit via the conference portal; attach the supplementary zip.

## 7. Post‑Submission Checklist
- Prepare a short video abstract (≤ 3 min) for the conference. Record a screen‑capture of the CLI and runtime metrics.
- Prepare a slide deck for the talk (intro, problem, system, results, future work).
- Share results on arXiv and bi-directional link from the GitHub repo.

## 8. Future Experiment Ideas
- Scale to TPC‑H or TPC‑DS full datasets and measure real‑world runtimes.
- Experiment with other LLMs (Claude, Llama) and compare cost‑performance trade‑offs.
- Add a feedback loop where humans confirm recommended rewrites to improve the prompt.
- Build a lightweight web dashboard for real‑time query monitoring.

---

*Prepared by Shouvik Sharma – Data Engineer, Chime*