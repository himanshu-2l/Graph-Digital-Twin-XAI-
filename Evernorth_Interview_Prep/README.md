# Evernorth Health Services (The Cigna Group) — Cybersecurity Technical Interview Preparation Suite

**Candidate:** Anshika Keshari (B.Tech CSE, KIIT University, CGPA: 8.32)  
**Target Role:** Cybersecurity Intern (Threat Management, Vulnerability Management & Security Operations)  
**Location:** Hyderabad Innovation Hub  
**Preparation Timeline:** 48 Hours (2-Day Intensive Master Plan)

---

## 📚 Study Roadmap & Document Index

The preparation documents are strictly numbered in chronological order. Follow this exact sequence from `01` to `06`:

| Step | Document | File (PDF) | LaTeX Source | Key Topics & Focus |
|:---:|:---|:---|:---|:---|
| **01** | **Master Preparation Plan** | [`01_START_HERE_2_Day_Preparation_Master_Plan.pdf`](./01_START_HERE_2_Day_Preparation_Master_Plan.pdf) | [`01_START_HERE...tex`](./01_START_HERE_2_Day_Preparation_Master_Plan.tex) | 48-Hour hour-by-hour study schedule, syllabus breakdown, 3 emergency interview rules. |
| **02** | **Company Research & Role Fit** | [`02_Evernorth_Company_Research_And_Role_Fit.pdf`](./02_Evernorth_Company_Research_And_Role_Fit.pdf) | [`02_Evernorth...tex`](./02_Evernorth_Company_Research_And_Role_Fit.tex) | Evernorth corporate profile (Express Scripts, Accredo, MDLIVE), 2024 healthcare threats (Change Healthcare breach fallout), JD alignment, 4-point intern contribution plan, 10 company Q&As. |
| **03** | **Projects Mastery & Bridging** | [`03_Technical_Projects_Mastery_And_Bridging.pdf`](./03_Technical_Projects_Mastery_And_Bridging.pdf) | [`03_Technical...tex`](./03_Technical_Projects_Mastery_And_Bridging.tex) | First-principles analogies (ICU & Airport customs), mathematical foundations (GraphSAGE, Integrated Gradients, SMOTE, XGBoost), bridging to healthcare IoMT & pharmacy fraud, 15+ grilling technical Q&As. |
| **04** | **Core CS & Technical Foundations** | [`04_Core_CS_And_Technical_Interview_Questions.pdf`](./04_Core_CS_And_Technical_Interview_Questions.pdf) | [`04_Core_CS...tex`](./04_Core_CS_And_Technical_Interview_Questions.tex) | Java OOP pillars with healthcare metaphors, interface vs abstract class, DSA (HashMaps, BFS/DFS, DP), OS (deadlocks, virtual memory), DBMS (ACID, B+ Trees), Networks (TLS 1.3 handshake), Azure Cloud (RBAC, Key Vault). |
| **05** | **Cybersecurity & Incident Response** | [`05_Cybersecurity_Domain_And_Incident_Response.pdf`](./05_Cybersecurity_Domain_And_Incident_Response.pdf) | [`05_Cybersecurity...tex`](./05_Cybersecurity_Domain_And_Incident_Response.tex) | Cyber Threat Intelligence (Pyramid of Pain, STIX/TAXII), MITRE ATT&CK Matrix, Vulnerability Management (CVSS v3.1, EPSS, CISA KEV), SOC Metrics (MTTD, MTTR, Dwell Time), NIST SP 800-61 IR Lifecycle, 6 healthcare scenarios. |
| **06** | **CheatSheet & Verbal Scripts** | [`06_Final_Review_CheatSheet_And_Interview_Day_Script.pdf`](./06_Final_Review_CheatSheet_And_Interview_Day_Script.pdf) | [`06_Final_Review...tex`](./06_Final_Review_CheatSheet_And_Interview_Day_Script.tex) | Master metrics cheat sheet, 90-sec verbatim opening script, "Why Evernorth" speech, Golden Bridge script, 4-step framework for unknown questions, STAR behavioral answers, 10 questions to ask interviewers. |

---

## 🎯 Candidate Master Metrics Cheat Sheet

- **Academic:** B.Tech CSE at KIIT University (2023–2027), **CGPA: 8.32**, zero backlogs.
- **Smart Grid Digital Twin:** IEEE 14-bus, GraphSAGE GNN, **<15ms mitigation**, FDIA detection ($a=Hc$), Integrated Gradients XAI, India–Norway INTPART project (IIIT Naya Raipur).
- **AML Fraud System:** 10,000+ synthetic transactions, **98.2% precision**, 97.4% recall, 15+ behavioral features, SMOTE without data leakage, XGBoost classifier.
- **Evernorth Scale:** 1 Billion+ annual prescriptions, 100M+ customers, Express Scripts PBM, Accredo Specialty Pharmacy, MDLIVE Telehealth, Hyderabad Innovation Hub.
- **Security Governance:** NIST CSF 2.0 (Govern, Identify, Protect, Detect, Respond, Recover), NIST SP 800-61 (4 IR phases), Zero Trust (Explicit verification, Least privilege, Assume breach).

---

## 🛠️ How to Compile LaTeX Files Locally

To recompile any of the LaTeX documents into PDF:
```bash
pdflatex -interaction=nonstopmode <Filename>.tex
pdflatex -interaction=nonstopmode <Filename>.tex  # Run twice to resolve hyperref outlines
```
*Compiler requirement: MiKTeX or TeX Live with standard packages (`tcolorbox`, `titlesec`, `enumitem`, `booktabs`, `tabularx`, `amsmath`, `amssymb`).*
