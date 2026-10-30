# MASTER PLAN — SUNRISE 2026 Revision
Repo: https://github.com/himanshu-2l/Graph-Digital-Twin-XAI-
Target: SUNRISE 2026 (4th Workshop on Secure and Resilient Digital Transformation of Healthcare), Springer CCIS, 12–15 pages incl. refs/appendices. Deadline: 5 Nov 2026.

This is one of five files. Read in this order:
1. `00_MASTER_PLAN.md` (this file) — decisions made, task list, order of operations.
2. `01_CODE_CHANGES.md` — exact code to add/modify, with an ablation rerun.
3. `02_PAPER_REVISION.md` — section-by-section text/math fixes answering every reviewer comment.
4. `03_HEALTHCARE_REPOSITIONING.md` — exact new text blocks for SUNRISE scope-fit.
5. `04_CCIS_FORMATTING.md` — template, page budget, submission checklist.

## Decisions made (so you don't need to re-litigate these)

| Issue | Decision | Why |
|---|---|---|
| "XAI attribution feedback" ablation (flagged by all 4 reviewers) | **Code-fix.** Implement a real, documented gradient-based attribution-gating mechanism, rerun only the Table V ablation rows it affects. | Cheapest high-value fix; graphs are tiny (14–30 nodes), CPU-trainable in minutes. Currently unreproducible — this is a credibility risk if left as-is. |
| "Admittance-weighted graph" vs. edge attributes unused by SAGEConv (Reviewer 4) | **Text-fix.** Rename to "topology-aware graph representation" everywhere; drop/qualify admittance-weighting language. | Rearchitecting the backbone (edge-aware conv) + rerunning every table (nominal, outage, 30-bus transfer, WLS comparison) in a week is too much surface area to risk new bugs this close to deadline. |
| Stealthy-FDIA threat model vs. load-scaling attack generator (flagged by all 4 reviewers) | **Relabel honestly + report actual χ² bypass rate** computed from existing data. No new attack generator. | Fastest fix that is still scientifically honest; doesn't require new data generation or retraining. |
| Healthcare repositioning | Proceed as scoped: new intro paragraph, short "Generalization to Healthcare CPS" subsection, 4–6 new related-work citations, optional subtitle. No results/experiments touched. | Protects against "bait-and-switch" criticism; matches what the editor asked for ("technically justified... does not change the paper's core contribution"). |
| CCIS template | Fetch officially (Overleaf gallery entry "Communications in Computer and Information Science"), do a full re-typeset from the current IEEEtran source — not a reformat. | CCIS and IEEEtran are structurally incompatible (single vs. two-column, different sectioning/reference style). |

## Task order for the coding/writing agent

1. Run the two small analysis scripts in `01_CODE_CHANGES.md` §1 (χ² bypass rate) and §2 (reproducibility/hyperparameter dump) — these only read existing data/checkpoints, no retraining, ~minutes.
2. Implement the attribution-gating mechanism in `01_CODE_CHANGES.md` §3, retrain the two required configurations (with-gating, without-gating = current baseline), regenerate just the Table V rows affected.
3. Start a **new** CCIS LaTeX project per `04_CCIS_FORMATTING.md` (don't try to reformat the IEEEtran file in place).
4. Port content section-by-section following `02_PAPER_REVISION.md`, applying every fix inline as you go (it is organized by paper section, in writing order).
5. Insert the healthcare material from `03_HEALTHCARE_REPOSITIONING.md` at the marked insertion points.
6. Update all tables/figures/abstract numbers that changed because of step 2 (ONLY Table V and any text referencing the attribution-feedback number — nothing else changes numerically).
7. Run the CCIS formatting checklist in `04_CCIS_FORMATTING.md` §Checklist before submitting.
8. Add a reproducibility statement + GitHub link (text given in `02_PAPER_REVISION.md` §I).

## Hard constraints to preserve
- Do **not** change any number in Tables I, II, III, IV, VI, VII, or Figs 3–6 — only Table V's two "Without XAI attribution feedback" / "Proposed GraphSAGE GDT" rows get real numbers from the rerun.
- Do **not** touch the core architecture, equations (1)–(15), or experimental protocol beyond what's specified in `01_CODE_CHANGES.md` §3.
- Do **not** claim healthcare validation/experiments anywhere — only a generalization argument, worded exactly as given in `03_HEALTHCARE_REPOSITIONING.md`.
- Page budget is 12–15 pages CCIS (single-column) — see `04_CCIS_FORMATTING.md` for where the extra length over the 6-page IEEE draft should go (it's mostly the new Section III-D reproducibility content + healthcare subsection + expanded limitations, not padding).
