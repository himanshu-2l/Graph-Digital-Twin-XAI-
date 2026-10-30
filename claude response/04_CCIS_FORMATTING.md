# Springer CCIS Formatting — template, page budget, submission checklist

## Template
- Do **not** reformat `docs/latex/Smart_Grid_GDT_IEEE_Paper.tex` in place — IEEEtran (two-column) and CCIS (single-column, different class file, different \maketitle/author-block macros, different reference style) are structurally incompatible. Start a **new** LaTeX project from the official Springer CCIS/LNCS-family template (Overleaf gallery: search "Communications in Computer and Information Science" or "Springer LNCS" — CCIS uses the same `llncs.cls` document class family as LNCS). Port content section-by-section rather than trying to patch the existing file.
- Keep the existing IEEE PDF/tex as a content source only — copy prose/equations/tables across, don't try to salvage the LaTeX structure.
- If no SUNRISE-specific Overleaf template link turns up, use Springer's generic CCIS author template from springer.com's "Computer Science Proceedings Guidelines" page — it's the same `llncs`-based template used across CCIS volumes.

## Page budget (12–15 pages CCIS, single-column, incl. references/appendices)
The current IEEE draft is ~6 pages two-column (dense). Single-column CCIS at the same word count typically runs noticeably longer per page of content, but you're still adding real material, not just padding:

| Addition | Approx. extra length |
|---|---|
| Healthcare intro paragraph + Section IX subsection + 4-6 new related-work citations | ~1–1.5 pages |
| Full hyperparameter list + reproducibility statement (Section V) | ~0.3 page |
| Digital twin state-sync subsection III-D (new equation + paragraph) | ~0.3 page |
| Expanded IV-D (two-mechanism explanation) | ~0.3 page |
| Healing-baseline comparison table + paragraph (Section VIII) | ~0.3 page |
| χ²-bypass-rate reporting paragraph (Section V-B) | ~0.2 page |
| Pulled-forward scope/limitations content into Section V (shortened, not duplicated) | ~0.2 page |
| **Consider an Appendix** with: full hyperparameter table, full per-seed results (not just mean±std), and the healing-baseline comparison detail | ~1–2 pages |

That gets you comfortably into the 12–15 page range from genuine content; don't artificially stretch margins/spacing or add filler — CCIS reviewers (and the editors who already flagged formatting in GC2026 review #1) will notice.

## Required elements checklist
- [ ] Abstract: single paragraph, 70–150 words, no citations.
- [ ] Keywords: comma-separated (not middot-separated).
- [ ] All authors: full name, affiliation, email, ORCID iD, exactly one marked corresponding author.
- [ ] Figures ≥600 dpi — check `/figures/*.png` resolution before reuse; re-export from `editable_figures/gdt_figure_matplotlib.py` or the `.drawio`/`.svg` sources at higher DPI if any fall short.
- [ ] Tables not in pictorial/image format (i.e., real LaTeX tables, not screenshotted images) — current repo tables already appear to be native LaTeX, carry that forward.
- [ ] All figures/tables/references numbered and explicitly cited in text.
- [ ] References: keep numbered IEEE-style citation markers (acceptable per Springer CS guidelines), add DOIs where available — go through refs [1]–[17] and look up DOIs for any missing them.
- [ ] Reproducibility/code-availability statement included (Section V, see `02_PAPER_REVISION.md`).
- [ ] No claim of healthcare experimental validation anywhere — scan the final draft for this before submitting.
- [ ] Initial submission: PDF only.
- [ ] Camera-ready (later, after editor feedback): source (tex or docx) + PDF in one zip, plus signed CCIS Consent to Publish form, plus Springer's "Checklist of items to be sent to the volume editor" (Section 9 of Springer's Guidelines for Authors of Proceedings — fetch this document directly from Springer's site, it's not reproduced here).

## Before sending the first revised draft back to the editors (per their email)
- Reply confirming the 5 Nov deadline and ask for: (a) the exact submission portal/track (EasyChair link, if any, for this extended round — the public CFP's EasyChair track closed with the Sep 25 deadline), (b) confirmation that CCIS is still the intended template for this round, (c) whether they want the PDF only or source files too at this stage (their email only asked for "the revised manuscript," which suggests PDF is sufficient pre-camera-ready).
