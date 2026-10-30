# Paper Revision — section-by-section, mapped to reviewer comments

Apply these in order while porting the IEEE draft (`docs/latex/Smart_Grid_GDT_IEEE_Paper.tex`) into the new CCIS project (see `04_CCIS_FORMATTING.md`). Each item cites which review(s) it answers so nothing gets dropped.

---

## Abstract
- No numeric changes except: if §3c in `01_CODE_CHANGES.md` produces a new attribution-feedback delta, do **not** put that number in the abstract (it's a secondary/ablation finding, keep abstract focused on headline detection/localization F1, which are unchanged).
- Add one clause at the end acknowledging the healthcare generalization, e.g.: "...while the underlying graph-based detection, explanation, and healing pipeline generalizes to other cyber-physical telemetry networks, including healthcare IT-OT infrastructure, as discussed in Section [X]." (Keep ≤150 words total, per CCIS limit — trim elsewhere if needed.)

## Section I (Introduction)
- Insert the new healthcare-framing paragraph from `03_HEALTHCARE_REPOSITIONING.md` §1 — placement: right after the existing motivation paragraph on stealthy FDIAs, before "Main Contributions."
- In "Main Contributions," soften "novelty" framing per R1-#1/R2-#1/R3-#1/R4-#1 (all four reviewers said the same thing): explicitly state the contribution is the **integration and reproducible benchmarking** of detection+localization+explainability+healing in one pipeline with a formally specified digital-twin synchronization model (new, see Section IV fix below) and a *validated* (not merely claimed) attribution-feedback mechanism — i.e., be honest that individual components (GraphSAGE, IG, WLS) are established, and frame the contribution as the systems-level integration + the two things that *are* new: (a) the formal digital-twin state-sync model, (b) the empirically validated attribution-gating result from the rerun.

## Section II (Related Work)
- Add the 4–6 healthcare-IT-OT security citations from `03_HEALTHCARE_REPOSITIONING.md` §3 as a new subsection "E. Security of Healthcare Cyber-Physical Systems."

## Section III (Mathematical Modeling & Threat Formulation) — R4-#6, all reviewers on III-C/V-B mismatch
- **Fix Eq. (7):** change from `r = ||z - h(x̂)||²₂ ≤ τ` to the covariance-weighted form consistent with Eq. (4):
  `r = [z - h(x̂)]ᵀ R⁻¹ [z - h(x̂)] ≤ τ`
- **Section III-C (Stealthy FDIA):** after Eq. (9), add one paragraph: "Equation (9) describes the idealized residual-preserving injection studied theoretically in the FDIA literature [cite Liu et al. 2011]. In Section V we additionally report results on a second, empirically generated attack family — AC-power-flow-consistent load disturbances — and explicitly measure what fraction of these satisfy the residual-preservation condition above, rather than assuming it; see Section V-B." This pre-empts the R1/R2/R3/R4 criticism by framing the gap honestly up front instead of letting the reviewer discover the mismatch.
- **New short subsection III-D, "Digital Twin State Synchronization"** (answers R3-#3/R4-#2 — "no unique mathematical model is provided"): add an explicit recursive update rule, e.g.:

  `x̂_twin(t) = x̂_twin(t−1) + K · [z(t) − h(x̂_twin(t−1))]`

  where `K` is a fixed gain (or the WLS gain matrix `(HᵀR⁻¹H)⁻¹HᵀR⁻¹` evaluated at the current operating point), run once per SCADA scan interval. State explicitly that this update *is* what Table V's "baseline tracking" ablation row removes (currently undefined in the draft) — i.e., removing it means the GNN only sees the instantaneous measurement vector `z(t)` with no twin-side temporal context. This single addition answers R3 recommended-change #2 and R4-#2 simultaneously.

## Section IV (Proposed Architecture)
- **IV-A/IV-C:** replace every instance of "admittance-weighted graph" with "topology-aware graph representation." Add one sentence acknowledging the scope explicitly: "The current GraphSAGE backbone aggregates over graph connectivity; branch admittance values (R_ij, X_ij, computed in Section IV-B) are retained in the data pipeline for future incorporation via edge-conditioned convolutions (e.g., NNConv), but are not consumed by the present mean-aggregation backbone." This directly and honestly resolves R4-#4 without requiring a rearchitecture.
- **IV-D (Operator Explainability):** rewrite to describe *two* distinct things clearly (answers R1-#5/R2-#3/R3-#4/R4-#5):
  1. A lightweight, training-time **Gradient × Input saliency gate** (Eq. new-16) that modulates node embeddings before the localization head only — give the exact gating equation from `01_CODE_CHANGES.md` §3a.
  2. The exact, 50-step **Integrated Gradients** computation (unchanged, Eqs. 16–17 as before) used strictly as the post-hoc, operator-facing explanation in Section VII, computed after training and never backpropagated into the model.
  State explicitly: "These are deliberately different mechanisms: the training-time gate uses a cheap single-step approximation for tractability, while the operator-facing explanation uses the exact path-integral formulation for its completeness guarantee. The ablation in Table V measures the training-time gate's contribution only."

## Section V (Experimental Setup)
- **V-A:** insert the full hyperparameter list from `01_CODE_CHANGES.md` §2 verbatim (layers, hidden dim, dropout, optimizer, lr, weight decay, epochs, batch size, loss weight, the actual 5 seed values).
- **V-B (Dataset Generation Protocol):** after describing the λ∈[1.5,2.0] load-scaling attacks, add: "We additionally quantify how many of these generated attacks satisfy the classical residual-preservation condition of Eq. (9): [X]% of attacked samples produce a normalized WLS residual below the χ² threshold τ (Section III-B), measured directly from the generated state estimates (see Appendix A for the measurement procedure)." — `[X]%` comes from `01_CODE_CHANGES.md` §1's script output. If the number is low, add one honest sentence: "This indicates that a meaningful share of our attack samples are detectable by classical bad-data detection and are better characterized as topology-propagating load disturbances than as fully residual-preserving stealthy FDIAs; Table [Y] reports detection performance separately for the subset that does satisfy the stealth condition where sample size permits." (Only include that last clause if there are enough stealthy-by-the-strict-definition samples to report separately — otherwise drop it and just state the measured rate.)
- Add a short **Reproducibility** paragraph at the end of V: "All code, trained checkpoints, and the dataset-generation pipeline are publicly available at [GitHub URL]." (Answers R3 recommended-changes #5.)

## Section VI (Numerical Results)
- **VI-A/VI-B/VI-C:** no numeric changes (Tables I–IV, Figs 3–4 stay as-is).
- **VI-C (Cross-grid transfer, IEEE 30-bus)** — R1-#6/R2-#4: rewrite the paragraph to separate detection and localization explicitly and stop implying uniform improvement:
  > "Fine-tuning substantially improves zero-shot detection (67.06% → 90.11% F1, outperforming training-from-scratch's 82.65%), demonstrating that detection-relevant representations transfer well across topologies. Localization transfer is more limited: fine-tuned localization F1 (80.06%) remains below the from-scratch baseline (83.58%), indicating that bus-level localization is more topology-specific and benefits less from pretraining than graph-level detection. We therefore moderate our scalability claim to detection transferability specifically, rather than general inductive scalability of the full joint task."
- **VI-D (Ablation Study):** replace the "Without XAI attribution feedback" row and corresponding text with the real numbers from `01_CODE_CHANGES.md` §3c, and rewrite the explanatory sentence to match the new IV-D framing (cheap training-time gate, not full IG backprop).
- **VI-E/VI-F:** no changes, except double-check Table VI's caveat (see next item).
- **Table VI caveat (R3 recommended-changes #4):** add a footnote under Table VI: "Boyaci et al. [10] and Yue & Qu [14] figures are as reported in their original publications under their own experimental protocols (different datasets/splits); they are included for context, not as a controlled head-to-head comparison." (Do this instead of reimplementing ARMA-GNN unless there's spare time before the deadline — reimplementing it properly is a multi-day task.)

## Section VII (Explainability Case Study)
- No numeric changes to Table VII. Add one sentence clarifying this is the exact post-hoc IG (not the training-time gate from IV-D), to avoid reintroducing the same ambiguity reviewers flagged.

## Section VIII (Closed-Loop Cyber-Mitigation) — R1-#3/R2-#5
- Add a small comparison: implement one baseline alternative to the historical-baseline substitution — simplest option is **linear interpolation** using the two nearest unaffected neighboring-bus readings, or a **persistence forecast** (last known-good value held constant). Report active-power MSE for both the existing method and this baseline in a small 2-row table. This directly answers "no comparison with other mitigation baselines" from two reviewers with minimal new code (a 10-line function, no retraining needed — this uses the already-trained model's localization output, just swaps the reconstruction step).
- Keep the existing single-Bus-5 case study, but add one sentence acknowledging scope: "This case study demonstrates feasibility for a single-bus attack; Section IX discusses the limitation that multi-bus coordinated attacks are not yet evaluated."

## Section IX (Discussion & Conclusions)
- Insert the new "Generalization to Healthcare Cyber-Physical Systems" subsection from `03_HEALTHCARE_REPOSITIONING.md` §2, placed right before "Future experiments."
- Pull forward (don't just leave at the end) two of the existing limitation sentences into Section V as scope statements, per `00_MASTER_PLAN.md`'s general guidance — leave shortened versions here, cross-referencing V.
- Add the reproducibility/code-availability sentence here too if not already stated in V (one mention is enough, pick whichever section reads better once typeset).

## Throughout
- Unify "reason" vs. "plan" cycle terminology — use **"Observe–Learn–Reason–Act"** everywhere (matches citations [16],[17] more closely than "Plan").
- Fix the Section IV-A typo mentioned by Reviewer 3 (locate it during the CCIS re-typeset — check the original IEEE .tex source around the digital-twin-layer description for the specific error).
- Clarify Eq. (14): state explicitly "Softmax is applied over the 2-class dimension independently for each node (per-node binary classification: benign vs. compromised), not across the node/bus dimension" — resolves R4-#7 in one sentence.
- Add ORCID iDs for all authors (CCIS encourages this).
