# Healthcare Repositioning — exact text blocks for SUNRISE scope-fit

Rule for all of this: **no new experiments, no claim of healthcare validation.** Every sentence below is framed as a generalization argument ("this transfers because..."), never as a result ("we tested this on..."). This is what keeps the repositioning "technically justified" without changing the core contribution, per the editor's own instruction.

---

## §1. New Introduction paragraph (insert after the stealthy-FDIA motivation paragraph, before "Main Contributions")

> Although this work is developed and validated on power-grid SCADA telemetry, the underlying problem — a cyber-physical system that streams heterogeneous sensor measurements from a topology that changes over time, where an adversary can inject false readings that evade residual-based anomaly checks — is not unique to the energy sector. Modern healthcare infrastructure exhibits the same structure: hospitals increasingly rely on networks of medical IoT devices (infusion pumps, patient monitors, implantable and wearable sensors) and building-level OT systems (HVAC, access control, power backup) that report continuous telemetry into centralized clinical and facilities-management systems [CITE-A][CITE-B]. These Internet-of-Medical-Things (IoMT) networks face an analogous threat: a spoofed vital-sign reading or falsified device telemetry can mislead clinical decision support or facility monitoring just as a falsified bus measurement misleads grid state estimation, and recent work has begun to specifically target false-data-injection detection in IoT-based medical devices [CITE-C]. A graph-structured, topology-invariant, explainable, and self-healing monitoring framework is therefore a natural fit for securing such heterogeneous, frequently-reconfigured healthcare sensor networks, not only power grids.

Replace `[CITE-A]`, `[CITE-B]`, `[CITE-C]` with entries from §3 below once added to the bibliography.

---

## §2. New subsection in Section IX (Discussion), placed before "Future experiments"

### IX-?. Generalization to Healthcare Cyber-Physical Systems

> The Cognitive Graph Digital Twin presented here was designed and evaluated on power-grid SCADA telemetry, and we make no claim of healthcare-specific validation in this paper. We outline here, as a methodological generalization argument, which components of the framework transfer directly to healthcare cyber-physical systems and which would require domain-specific adaptation, consistent with this workshop's focus on secure and resilient digital transformation of healthcare.
>
> **Components that transfer directly:**
> - *Graph representation of heterogeneous sensor networks:* just as buses and transmission lines form a graph, medical devices, gateways, and monitoring stations in a hospital network form a naturally graph-structured topology that changes as devices are added, removed, or reconfigured across wards — the same motivation that drove our choice of a topology-invariant GNN backbone over fixed-input architectures.
> - *Joint detection and localization:* identifying not only that an anomaly occurred, but which specific device or channel is responsible, is at least as important in a clinical setting as in a grid — a false alarm at the wrong bed has direct patient-safety consequences.
> - *Operator-facing explainability:* Integrated Gradients' per-channel attribution (Section VII) addresses a need that is, if anything, stronger in healthcare: clinicians and biomedical engineering staff require an auditable reason for any automated flag before acting on it, paralleling the explainability requirements increasingly discussed for medical AI systems generally [CITE-D].
> - *Closed-loop quarantine-and-substitute recovery:* the pattern of isolating a compromised channel and substituting a principled estimate (Section VIII) generalizes structurally to quarantining a compromised device feed and substituting a clinically validated fallback.
>
> **Components that require healthcare-specific adaptation, not a direct port:**
> - *Measurement model:* our state estimator relies on AC power-flow physics (Eqs. 1–6); patient vital signs and device telemetry follow physiological and device-specific dynamics rather than electrical network equations, so the measurement function `h(x)` and its Jacobian would need to be re-derived per device class rather than reused.
> - *Autonomous mitigation safety constraints:* silently substituting a reconstructed value is defensible for a grid load estimate, but substituting a patient vital-sign reading — even temporarily and even when flagged as compromised — carries direct clinical-safety and regulatory implications (e.g., HIPAA, device-safety certification) that have no equivalent in the grid setting; any healthcare adaptation of Section VIII's healing module would need a human-in-the-loop confirmation step rather than fully autonomous substitution.
> - *Threat model specifics:* healthcare IoMT attack surfaces (e.g., compromised wireless gateways, firmware tampering, supply-chain-introduced vulnerabilities in medical devices [CITE-E]) differ from grid RTU/PMU compromise, and would need their own stealth-condition analysis analogous to Section III-C rather than reusing the WLS-residual formulation as-is.
>
> We view this cross-domain structural fit — rather than a direct transplant — as the appropriate first step toward adapting cognitive digital twin architectures to healthcare resilience, consistent with related digital-twin-for-healthcare-resilience work presented at this workshop [CITE-F].

---

## §3. New Related Work subsection II-E, "Security of Healthcare Cyber-Physical Systems"

Add these citations to the bibliography and write 1 sentence per paper. Candidates found via search (verify access/exact venue before camera-ready; arXiv preprints should be checked for a published venue if one exists by submission time):

- **[CITE-C]** DSTAN-Med: dual-channel spatiotemporal attention with physiological-plausibility filtering for false data injection attack detection in IoT-based medical devices. (arXiv, 2026 — directly on-topic: FDIA detection specifically in medical IoT telemetry, closest analog to this paper's problem in the healthcare domain.) — https://arxiv.org/pdf/2605.14165
- **[CITE-B]** Systems-theoretic and data-driven security analysis in ML-enabled medical devices. (arXiv, 2025.) — https://arxiv.org/abs/2506.15028
- **[CITE-A]** Cyber security of OT networks: a tutorial, survey of attacks, and overview of current defense tools/protocols/challenges. (arXiv, 2025 — general IT-OT security survey, cite for the IT-OT convergence framing that applies to both grid and hospital OT.) — https://arxiv.org/pdf/2502.14017
- **Digital twin-based topology fingerprinting for detecting false data injection attacks in cyber-physical systems** (general CPS, not healthcare-specific, but directly relevant methodologically — digital-twin + FDIA detection). — https://mdsoar.org/items/49702561-fe2b-4e88-bba9-6a46ccbce970/full
- **[CITE-F]** The Adaptive Cognitive Digital Twins (ACDT) architecture for resilient healthcare infrastructure, introduced at SUNRISE 2024 and extended in the SUNRISE 2025 proceedings (CCIS vol. 2867, pp. 43–79). This is the most important citation to add — it's prior work from the exact workshop you're submitting to, on a directly related "cognitive digital twin for healthcare resilience" theme, and citing it signals you've engaged with the venue's own prior work. Verify exact author/title via SpringerLink conference page (link.springer.com/conference/sunrise) before finalizing the reference entry.
- **[CITE-D]** (to source) — one general explainable-AI-in-healthcare/clinical-trust citation; you likely already have IG/XAI references in your current bibliography ([7], [15]) — check whether either can be reused/extended here instead of adding a new one, to save a reference slot.
- **[CITE-E]** (to source) — one citation specifically on medical device/IoMT supply-chain or firmware attack surface, if you want this sentence to carry a concrete citation rather than being an assertion. A quick targeted search ("medical device firmware supply chain attack survey") should turn up a usable survey paper; not sourced yet in this pass.

**Agent note:** I flagged which citations are "to source" vs. already-found-and-verifiable — don't fabricate DOIs/page numbers for the ones marked to-source; do a fresh search for those two before camera-ready, and double check the SUNRISE 2024/2025 ACDT paper's exact author list and title from SpringerLink rather than the short description found via search snippet.

---

## §4. Optional title tweak

Current: *"A Cognitive Graph Digital Twin for Adaptive Cyber Resilience in Smart Grid Networks"*

Suggested (keeps grid work primary, signals healthcare relevance for scope-matching reviewers):
*"A Cognitive Graph Digital Twin for Adaptive Cyber Resilience: A Smart-Grid Case Study with Implications for Healthcare Cyber-Physical Systems"*

This is optional — if it feels like it overclaims given the content is still 100% grid experiments, keep the original title and rely on the abstract clause + intro paragraph + Section IX subsection to carry the scope-fit signal instead. Your call; either is defensible.
