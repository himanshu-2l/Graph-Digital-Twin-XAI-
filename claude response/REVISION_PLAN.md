# Revision Plan — Cognitive Graph Digital Twin paper → SUNRISE 2026

Target: 4th SUNRISE Workshop (Secure and Resilient Digital Transformation of Healthcare), co-located with NIKT 2026, Levanger, Norway. Springer CCIS proceedings. 12–15 pages incl. references/appendices. Deadline given to you: **5 Nov 2026**.

> ⚠️ Flag: the public SUNRISE 2026 CFP I found lists submission deadline **25 Sep 2026** (already passed), notification 18 Oct, camera-ready 26 Oct, workshop day 25 Nov 2026 (source: cyballiance.nr.no/sunrise-2026). Your "5 Nov 2026" deadline is almost certainly a **personal/invited extension** from the organizers (the email reads like a direct invitation to resubmit, with the editors offering a feedback pass before camera-ready) — not the public open-call deadline. Treat the editor's email as authoritative, but it would be worth a 1-line reply confirming the Nov 5 date and asking for the current CCIS template link/EasyChair submission track, since the public CFP page doesn't mention a second round.

---

## 0. Repo audit — before touching the writing (do this first)

I pulled `himanshu-2l/Graph-Digital-Twin-XAI-` and checked it against the paper's claims. Three things need a decision from you **before** I draft text, because they determine whether we fix the paper to match the code, or fix the code to match the paper:

1. **The "XAI attribution feedback" ablation (Table V) is not implemented anywhere in the repo.** `explainability.py` only runs Integrated Gradients post-hoc on the already-trained graph-level detector — it never touches the localization head, and there is no training-time mechanism that routes IG attributions into `node_classifier`. All four reviewers independently flagged this exact inconsistency. Right now the paper's strongest secondary finding (+5.52pp from attribution feedback) is not reproducible from the public code. **This needs either: (a) actually implement a feedback mechanism and rerun the ablation, or (b) remove/relabel this claim honestly** (e.g., re-describe it as a hypothesis for future work, or re-run the ablation as "IG-guided feature masking" if that's closer to what was actually done).
2. **Edge attributes (`R_ij`, `X_ij`) are computed in `data_generation.py` but never consumed by the model.** `model.py`'s `SAGEConv(in_channels, hidden_channels)` only takes `(x, edge_index)` — the admittance-weighted edge features are discarded. This exactly matches Reviewer 4's point: the "admittance-weighted graph" claim isn't reflected in the architecture. Fix: either (a) switch to an edge-feature-aware layer (e.g., `NNConv`, `GINEConv`, or a custom SAGEConv variant that concatenates `e_ij` into the message), retrain, and report real numbers, or (b) drop the "admittance-weighted" language and accurately describe the model as topology-aware (connectivity-only).
3. **No ablation-runner script exists** (no `ablate.py` / `experiments/ablation.py`). Table V numbers aren't reproducible from a script I can find. Same for the "digital twin baseline tracking" ablation — I don't see a formal, separate baseline-tracking module either; it looks folded informally into `cyber_mitigation_demo.py`.

**My recommendation:** given the Nov 5 deadline, don't try to rebuild the GNN architecture (edge-aware conv) and rerun 5-seed experiments in a week unless you have GPU time already lined up. Instead:
- Implement the IG→localization feedback for real (it's a small, well-scoped change: use attribution scores as an auxiliary input/mask to the node classifier, or as an auxiliary loss term) and rerun just that ablation row — this directly answers the #1 most-repeated reviewer complaint and takes a few hours of compute.
- For the edge-attribute gap, the honest, low-risk fix is to **soften the claim in text** (say "topology-aware" instead of "admittance-weighted") rather than rearchitect under deadline pressure — unless you want to actually add edge-feature aggregation, which I can help implement if you have a day of GPU time to spare.

Tell me which of these two issues you want to code-fix vs. text-fix before I touch the manuscript — it changes what Sections III/IV/VI say.

---

## 1. Fixes that address reviewer comments (apply regardless of venue)

### A. Reconcile threat model vs. attack generation (R1-#2, R2-#2, R3-#2, R4-#3) — raised by literally every reviewer
- Current text defines stealthy FDIA via the residual-preserving vector `a = h(x+c) - h(x)` (Eq. 8–9), but the dataset (`data_generation.py`) generates attacks by scaling a bus's load by λ∈[1.5,2.0] and re-running AC power flow — a real physical disturbance, not a residual-preserving injection.
- **Fix:** Pick one of two honest paths:
  1. Relabel Section III-C/V-B: call these "load-manipulation disturbances / physically-propagated anomalies," not "stealthy FDIA," and empirically report the χ² bypass rate for these samples (i.e., show what fraction actually keep `r ≤ τ`) rather than assuming it.
  2. Add a second, genuinely residual-preserving attack generator (this is the rigorous option — a small amount of linear algebra against the measurement Jacobian) and report results on both attack families.
- Given the deadline, Option 1 (honest relabeling + reporting actual bypass rate from existing data) is the realistic one for this cycle.

### B. Define the "XAI attribution feedback" mechanism formally, or remove the claim (R1-#5, R2-#3, R3-#4, R4-#5)
- See repo audit #1 above. Whatever you decide, Section IV-D needs an explicit equation/algorithm box describing exactly how attribution scores enter the localization pipeline (loss term, gating, or feature concat) — "it helps" is not acceptable to any of the four reviewers.

### C. Fix the Eq. (4) vs. Eq. (7) WLS inconsistency (R4-#6)
- Eq. 4 uses covariance-weighted residual `[z-h(x)]ᵀR⁻¹[z-h(x)]`; Eq. 7 uses unweighted Euclidean norm. Pick the weighted form consistently (it's the textbook-correct one) and fix Eq. 7 to `[z-h(x̂)]ᵀR⁻¹[z-h(x̂)] ≤ τ`. One-line LaTeX fix, but matters for rigor.

### D. Clarify Eq. (14) Softmax dimension (R4-#7)
- State explicitly whether `Softmax` in `y_node = Softmax(W_node H)` is applied per-node over {benign, compromised} (i.e., `dim=-1` over the 2-class axis — which is what `model.py`'s `F.cross_entropy` + 2-output `Linear` layer actually does) or across buses. Spell this out; it also resolves the ambiguity reviewers raised about transfer to the 30-bus system.

### E. Separate detection vs. localization in cross-grid transfer claims, and moderate the "zero-shot scalability" language (R1-#6, R2-#4)
- Current: zero-shot 30-bus detection F1 67.06%, localization F1 17.77%; fine-tuned detection 90.11% (> from-scratch 82.65%) BUT fine-tuned localization 80.06% (< from-scratch 83.58%).
- The paper currently claims transfer learning "outperforms training from scratch" without noting localization is actually *worse* after fine-tuning. **Fix:** report both metrics side by side honestly, explicitly state the detection/localization split, and soften "demonstrates transferable graph representations" to something like "detection representations transfer; localization requires grid-specific fine-tuning, indicating transfer benefits are task-dependent."

### F. Strengthen/caveat the self-healing and dataset-realism claims (R1-#3/#4, R2-#5/#6)
- The paper already lists these as limitations in Section IX, which is good — reviewers want them moved forward and made more concrete, not just acknowledged at the end. **Fix:**
  - In the healing section (Section VIII), explicitly compare the historical-baseline substitution against at least one standard alternative (e.g., simple linear interpolation or a persistence forecast) even if only as a small additional table — this directly answers R1-#3/R2-#5's "no comparison with other mitigation baselines."
  - Add 2–3 sentences in the dataset section candidly scoping what pandapower-synthetic data does/doesn't capture (you already have good limitation language in Section IX — pull some of it forward into Section V as a stated scope boundary, not just a post-hoc limitation).

### G. Define the digital-twin layer formally (R3-#3, R4-#2)
- "Continuously synchronized," "observe-learn-reason-act" are asserted but never mathematically specified. **Fix:** add one small subsection with an explicit state-update rule for the virtual twin, e.g. a synchronization equation like `x̂_twin(t) = x̂_twin(t-1) + K·(z(t) - h(x̂_twin(t-1)))` run every SCADA scan, plus a one-paragraph description of what the "baseline tracking" ablation row in Table V actually removes (currently undefined — this is also needed to make the repo's cyber_mitigation_demo.py officially "the digital twin module").

### H. Fix the admittance-weighted graph / GraphSAGE mismatch (R4-#4)
- See repo audit #2. Text fix (recommended for this cycle) or code fix (if you have time) — pick one and I'll align Sections III-A/IV-C accordingly.

### I. Minor fixes (all reviewers, low effort, do these regardless)
- Report full hyperparameters: GraphSAGE layer count (3, per `model.py`), hidden dim (64), dropout (0.2), optimizer (Adam, lr=0.005, wd=1e-4), epochs (60), loss weight λ_loc=1.5 — all currently missing from the text (R3-#4).
- Add a reproducibility/code-availability statement pointing to the GitHub repo (R3-#4, R3 recommended changes #5).
- Clarify Table VI: Boyaci et al. / Yue & Qu numbers come from their own papers under their own setups, not a reimplementation under identical conditions — either re-implement ARMA-GNN under your exact pipeline (if time allows) or add an explicit caveat sentence under the table (R3 recommended changes #4).
- Fix the typo in Section IV-A and unify "reason" vs. "plan" cycle terminology throughout (pick one, I'd suggest "Observe–Learn–Reason–Act" since that's the more common Cognitive Digital Twin phrasing in your own citations [16],[17]) (R3 recommended changes #5).

---

## 2. Repositioning for SUNRISE's healthcare scope (without changing the core contribution)

SUNRISE's listed topics are healthcare application security/privacy, healthcare supply-chain security, human factors, secure IT-OT for healthcare, digital transformation risk management, and health-systems digital resilience. Your contribution — a graph-based cognitive digital twin for anomaly detection/localization/explainability/healing over sensor telemetry on a physical infrastructure network — is a **methodology transplant**, not a healthcare paper as-is. That's fine and common for this workshop (last year's CCIS volume explicitly had a "Cognitive Digital Twins for Resilient Systems" track that is domain-general), but it needs explicit bridging, not a global search-and-replace of "grid" with "hospital."

Concretely, keep every equation, architecture, and smart-grid experiment exactly as-is (that's the technically-justified part — nothing here invalidates your results), and add:

1. **New framing paragraph in the Introduction** explicitly mapping the method to healthcare IT-OT: hospitals run analogous sensor/actuator networks — medical IoT devices, infusion pumps, patient monitors, building/HVAC OT systems — reporting telemetry into a central system that is just as vulnerable to stealthy false-data injection (e.g., a spoofed vital-sign reading or falsified device telemetry) as SCADA measurements are in a grid. Cite healthcare-IoT security literature (I can source 3–4 recent papers on FDIA/spoofing in medical IoT / BAN / smart-hospital OT networks for this).
2. **A short "Generalization to Healthcare Cyber-Physical Systems" subsection** (half a page, in Discussion/Conclusion) stating precisely what transfers directly (graph representation of heterogeneous sensor networks, topology-invariant detection, explainable per-sensor attribution for clinician/operator trust, closed-loop quarantine-and-substitute recovery) and what would need healthcare-specific adaptation (different measurement models than AC power flow — e.g., patient vitals have physiological rather than electrical constraints; different regulatory/safety requirements for autonomous "healing" actions, i.e., you cannot silently substitute a patient's vital-sign reading the way you substitute a load baseline — HIPAA/clinical-safety implications belong here).
3. **Related-work addition**: 4–6 references on security of healthcare IT-OT / medical device networks / digital twins in healthcare, positioning your GraphSAGE+IG+healing pipeline as a transferable blueprint, consistent with SUNRISE's own framing of digital twins as a cross-cutting resilience tool (this also lets you cite the CybAlliance/NORCICS-affiliated prior SUNRISE papers, which workshop reviewers tend to like seeing).
4. Title tweak (optional but worth considering): something like *"A Cognitive Graph Digital Twin for Adaptive Cyber Resilience: A Smart-Grid Case Study with Extensions to Healthcare Cyber-Physical Systems"* — keeps the grid work front and center (honest) while explicitly signaling the healthcare relevance for SUNRISE's scope-fit reviewers.

This reframing is "technically justified" in the sense the editor asked for: it does not claim healthcare validation, doesn't touch results, and is explicit that the healthcare content is a generalization argument, not a new experiment — which protects you from a reviewer calling it a bait-and-switch.

---

## 3. Springer CCIS formatting requirements

- **Template:** Use the official Springer CCIS LaTeX (or Word) template — not the IEEE two-column `IEEEtran` template your current repo uses (`docs/latex/Smart_Grid_GDT_IEEE_Paper.tex`). CCIS is single-column, different margins/fonts, different reference style. This is a full re-typeset, not a reformat.
- **Length:** 12–15 pages including references/appendices (you asked for this explicitly — your current IEEE version is ~6 pages two-column, so expanaded healthcare framing + more hyperparameter/reproducibility detail + possibly an appendix with full tables will usefully fill the extra space rather than requiring padding).
- **Abstract:** 70–150 words, no citations, self-contained.
- **Keywords:** separated by commas (not middots) per current Springer CS-proceedings guidance.
- **Figures:** ≥600 dpi, numbered, captioned, referenced in text. Your `/figures` PNGs should be checked for resolution before reuse.
- **References:** Springer encourages DOIs where available; numbered or author-year both acceptable — stay consistent with your existing numbered IEEE style, just add DOIs where you have them.
- **Author info:** full name, affiliation, email, ORCID for all authors, one designated corresponding author.
- **Submission:** initial submission as PDF only, built from the CCIS template (non-compliant formatting risks outright rejection per the series' standard author guidelines) — camera-ready later needs both source (tex/docx) + PDF in one zip, plus a signed CCIS Consent to Publish form.
- I haven't found a SUNRISE-specific submission portal/EasyChair link for this extended deadline — worth asking the editors for the exact track/portal when you reply confirming Nov 5.

---

## 4. What I need from you to proceed

1. Decision on repo audit items #1 (IG feedback) and #2 (edge attributes): text-fix or code-fix? This gates what I write in Sections III/IV/VI.
2. Confirmation you want the Option-1 (relabel, not re-derive) fix for the stealthy-FDIA/data-generation mismatch (1.A above) — this is the fastest honest path given the Nov 5 deadline.
3. OK on the healthcare-repositioning approach in Section 2 (new intro paragraph + short generalization subsection + related work, no results changes, optional title tweak)?
4. Do you have the Springer CCIS LaTeX/Word template already, or should I fetch it (Springer provides it on their site / Overleaf has an official CCIS template gallery entry)?
5. Any GPU/compute time available before Nov 5 if you want a real code fix for item #1 (IG→localization feedback) rather than a text-only fix?

Once you answer these, I'll draft the revised manuscript section-by-section in the CCIS template.
