# IEEE BigData 2026 Arizona Submission Package

This folder contains the IEEE BigData 2026 version of the query-monitoring paper.

## Files

- `paper_ieee_bigdata2026.tex`: IEEE-style LaTeX manuscript.
- `paper_ieee_bigdata2026.md`: Markdown source draft.
- `references.bib`: BibTeX references used by the LaTeX manuscript.
- `artifact_note.md`: artifact/reproducibility statement and script mapping.
- `submission_checklist.md`: IEEE BigData 2026 compliance checklist.
- `figures/architecture.md`: source note for a future architecture figure.

## Build

From this folder, compile with:

```powershell
pdflatex paper_ieee_bigdata2026.tex
bibtex paper_ieee_bigdata2026
pdflatex paper_ieee_bigdata2026.tex
pdflatex paper_ieee_bigdata2026.tex
```

If `IEEEtran.cls` is missing, install the IEEE LaTeX template from:

https://www.ieee.org/conferences/publishing/templates.html

## Submission Notes

- IEEE BigData 2026 is single-blind, so author identity and repository URL can remain visible.
- Full paper limit is 10 IEEE two-column pages including references.
- Author affiliation in the manuscript is K. J. Somaiya College of Engineering, India.
