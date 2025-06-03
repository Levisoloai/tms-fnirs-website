# Adaptive Protocol-Generation Engine (APGE): Graph-Driven, Evidence-Weighted Personalization of TMS & Other Neuromodulation Therapies

## 1. Executive Summary (≈ 1 page)
The field of neuromodulation, while promising, currently faces a significant challenge: treatment protocols, particularly for conditions like Transcranial Magnetic Stimulation (TMS) resistant depression (TRD), Obsessive-Compulsive Disorder (OCD), and Post-Traumatic Stress Disorder (PTSD), are largely standardized. This "one-size-fits-all" approach contributes to non-response rates ranging from 30% to 50%, representing a substantial portion of patients who do not receive the full benefits of these advanced therapies. This gap highlights a critical need for personalized treatment strategies that can adapt to individual patient neurophysiology and clinical presentations.

Our solution is the Adaptive Protocol-Generation Engine (APGE), an innovative system designed to address this personalization gap. APGE leverages a sophisticated graph-based model, ingesting and analyzing a vast corpus of peer-reviewed research and real-world clinical outcomes. By structuring this information into a dynamic knowledge graph, APGE can rapidly generate patient-specific neuromodulation parameters, tailored to individual needs, within seconds. This approach moves beyond static protocols to offer a dynamic, evidence-based tool for clinicians.

The implementation of APGE is poised to have a transformative impact on neuromodulation therapy. We anticipate significantly faster patient response rates and a considerable reduction in the retreatment burden currently faced by clinics and patients. Furthermore, APGE's architecture lays a crucial foundation for the development of fully closed-loop TMS-fNIRS systems, where treatment parameters can be adjusted in real-time based on direct neurophysiological feedback, heralding a new era of precision in brain stimulation therapies.

To realize the full potential of APGE, we are seeking seed funding to finalize development, expand our data acquisition efforts, and initiate pilot clinical trials. We are also actively looking for data-sharing partners and clinical trial sites to help validate and refine APGE's capabilities, ensuring its robust real-world efficacy and facilitating its translation into widespread clinical practice.

## 2. Market & Clinical Need

| Metric                               | Current State                       | APGE Target                          |
|--------------------------------------|-------------------------------------|--------------------------------------|
| Global TMS market size (2024)        | $1.3 B                              | CAGR > 10 %                          |
| Average MDD response after 6 wks rTMS | 58 %                                | 70 %+ with APGE-guided targeting     |
| Failed first-line neuromod therapies | 35 %                                | < 20 % (adaptive protocols)          |

### Gap Analysis: The Limitations of Standardized Protocols
The prevalent use of standardized Transcranial Magnetic Stimulation (TMS) protocols, such as the common 10 Hz stimulation of the left dorsolateral prefrontal cortex (DLPFC) for depression, represents a significant gap in current neuromodulation practice. While this approach has demonstrated efficacy for a subset of patients, its "one-size-fits-all" nature doesn't account for the vast inter-individual variability in brain structure, function, and underlying pathology. Factors contributing to the failure of such standard protocols include:
    *   **Neuroanatomical Variability:** Differences in skull thickness, cortical folding, and precise location of target areas like the DLPFC can lead to suboptimal coil placement and E-field delivery when using generic coordinates.
    *   **Physiological Differences:** Individual variations in cortical excitability, neurotransmitter levels, and network connectivity mean that a standard stimulation frequency or intensity may be sub-therapeutic for some and excessive for others.
    *   **Heterogeneity of Illness:** Conditions like Major Depressive Disorder (MDD) are increasingly understood as heterogeneous, with different subtypes potentially responding to different stimulation parameters or targets. A single protocol is unlikely to address this clinical diversity effectively.
    *   **Lack of Real-time Feedback:** Standard protocols are typically administered without concurrent neurophysiological monitoring, missing opportunities to adjust parameters based on the brain's actual response to stimulation.
This lack of personalization contributes directly to the significant non-response rates observed in clinical practice and underscores the urgent need for adaptive, patient-tailored approaches.

### Competitive Landscape
The current market for TMS and related neuromodulation technologies includes several key players providing advanced hardware and treatment systems. Companies such as MagVenture (with its MagPro line and neural navigator), Axilum Robotics (offering robotic TMS solutions), and BrainsWay (known for its Deep TMS H-coils) have made significant contributions to the field by improving the precision, comfort, and range of TMS applications. Other neuronavigation systems and treatment planning software also exist, aiming to enhance targeting accuracy.

However, a critical distinction lies in the optimization of treatment *protocols* at the individual patient level. While existing systems offer sophisticated methods for delivering TMS, they generally do not incorporate dynamic, data-driven engines for personalizing the actual stimulation parameters (frequency, intensity, pulse patterns, specific target refinement) based on a comprehensive synthesis of patient-specific data and the latest evidence. APGE aims to fill this void by providing an intelligent layer that complements these hardware advancements, focusing on optimizing the *what* and *how* of stimulation for each unique patient, rather than solely the *where*. This positions APGE not necessarily as a direct competitor to hardware manufacturers but as a crucial enabling technology that can integrate with and enhance the value of existing and future neuromodulation systems.

## 3. Scientific Background
### 3.1 Graph Representations in Precision Psychiatry
The application of graph theory and network models to psychiatry is a rapidly advancing field, offering powerful tools to understand the complex interplay of symptoms, neurobiology, and treatment responses. Graph representations allow for the modeling of psychiatric conditions not as monolithic entities, but as interconnected networks of symptoms, genetic predispositions, environmental factors, and neurobiological markers. Precedents, such as the work by Camci & Krystal (2023), demonstrate the utility of network approaches in identifying treatment targets and predicting outcomes in precision psychiatry. APGE builds upon this foundation by using a graph database to explicitly model the relationships between diagnoses, symptoms, neurophysiological targets, stimulation parameters, and the supporting evidence from scientific literature and clinical data. This enables a nuanced, data-driven approach to personalizing neuromodulation therapy.

### 3.2 Dose-Response Relationships in rTMS
The efficacy of repetitive Transcranial Magnetic Stimulation (rTMS) is critically dependent on the "dose" delivered to the patient. This dose is a multifactorial concept encompassing parameters such as the strength of the induced electric field (E-field) at the cortical target, the number of pulses per session and per train, the frequency of stimulation (e.g., high-frequency excitatory vs. low-frequency inhibitory), and the inter-train interval. Different symptom clusters and underlying neuropathologies may exhibit varying sensitivities to these parameters. For instance, the optimal E-field strength and pulse count required to alleviate anhedonia might differ from those needed to address cognitive deficits in depression. Understanding these dose-response relationships is crucial for optimizing rTMS protocols. APGE aims to codify these complex relationships within its graph model, allowing for recommendations that are sensitive to the specific symptom profile of the patient.

### 3.3 Real-Time Hemodynamic and Electrophysiological Biomarkers
The integration of real-time brain activity monitoring with neuromodulation techniques offers an unprecedented window into the immediate effects of stimulation. Technologies like concurrent TMS-fNIRS (Functional Near-Infrared Spectroscopy) and TMS-EEG (Electroencephalography) allow for the measurement of hemodynamic and electrophysiological responses to TMS pulses, respectively. These responses can serve as valuable biomarkers of cortical excitability, reactivity, and connectivity. For example, changes in oxygenated hemoglobin (Δ[HbO]) measured by fNIRS post-stimulation can indicate the engagement of the targeted cortical area, while EEG can reveal alterations in neural oscillations and evoked potentials. Such biomarkers are pivotal for understanding target engagement, individualizing treatment parameters, and form the basis for future closed-loop adaptive systems where stimulation can be adjusted dynamically based on direct neurophysiological feedback. APGE is designed to incorporate these biomarker data points as evidence, further refining its personalized recommendations.

### 3.4 Clinical Guideline Drift and the Evidence-to-Practice Lag
A persistent challenge in clinical medicine, including neuromodulation, is the "guideline drift" phenomenon, where established clinical guidelines may not reflect the most current scientific evidence. The traditional process of evidence synthesis, guideline formulation, and dissemination can take many years, often estimated around a 9-year lag between research findings and their integration into routine clinical practice. This delay means that patients may not always benefit from the latest advancements in treatment protocols. APGE addresses this issue by creating a dynamic system that can incorporate new evidence much more rapidly. Through its automated literature scraping and evidence-weighting mechanisms, APGE aims to significantly reduce this evidence-to-practice gap, ensuring that protocol recommendations are based on the most up-to-date understanding available.

## 4. APGE Architecture
The Adaptive Protocol-Generation Engine (APGE) is built upon a modular architecture designed for scalability, maintainability, and the seamless integration of new evidence and data sources. Key components include:

### 4.1 Data Layer
At the core of APGE lies a robust **Neo4j graph database**. This choice of technology is pivotal, as it allows for the intuitive modeling of complex relationships inherent in medical knowledge. The graph schema is structured around several key node types:
    *   **Diagnosis:** Represents clinical diagnoses (e.g., Major Depressive Disorder, OCD).
    *   **Symptom:** Describes specific clinical symptoms or symptom clusters (e.g., Anhedonia, Rumination).
    *   **Target:** Refers to neuroanatomical targets for stimulation (e.g., Left DLPFC, Orbitofrontal Cortex).
    *   **StimParams:** Encapsulates specific stimulation parameters (e.g., 10 Hz frequency, 120% MT intensity, 3000 pulses).
    *   **Evidence:** Represents pieces of scientific literature or clinical data supporting relationships between other nodes (e.g., a specific study linking a Symptom to a Target, or a Target to effective StimParams). This node includes metadata such as study type, effect size, and publication details.
All nodes and relationships are versioned (current schema version: **v {SCHEMA_VERSION}**) to ensure traceability and accommodate updates as new research emerges.

### 4.2 ETL Pipeline (Extract, Transform, Load)
APGE incorporates an automated ETL pipeline to ingest and process data from various sources. This pipeline is designed to handle:
    *   **Structured Protocols:** Existing TMS protocols often described in YAML or JSON formats.
    *   **Scientific Literature:** Peer-reviewed articles, meta-analyses, and clinical trial results (initially via manual curation, with future automation for scraping and NLP-based extraction).
    *   **Real-World Data:** Anonymized clinical outcomes and patient characteristics (from data-sharing partners).
Data is processed through Data Access Objects (DAOs) that transform the incoming information into graph structures. These are then translated into **Cypher queries** (Neo4j's query language) to populate and update the graph. The pipeline enforces strict data integrity constraints, including unique identifiers for all entities and systematic versioning of evidence and protocol components.

### 4.3 Recommendation Engine
The recommendation engine is the analytical heart of APGE. When presented with patient-specific information (diagnosis, key symptoms, clinical history), it queries the graph database and applies a **multi-objective scoring algorithm** to identify and rank potential TMS protocols. The scoring considers several factors:
    *   **`evidence_weight`:** Quantifies the strength and quality of scientific backing for a given protocol or its components, often derived from meta-analysis effect sizes or GRADE scores (see Algorithms section).
    *   **`patient_similarity`:** Utilizes an embedding of the patient's phenotypic vector (a representation of their clinical characteristics) to find similar patient profiles within the dataset and identify protocols that were effective for them.
    *   **`risk_penalty`:** Incorporates factors that might increase risk or indicate contraindications, such as patient age, known comorbidities, or a low seizure threshold, adjusting scores accordingly.

### 4.4 API Layer
APGE exposes its functionalities through a **FastAPI-based API layer**. This provides a set of well-defined endpoints for interaction with other systems, including the clinician-facing front-end. Key endpoints include:
    *   `/recommendations`: Accepts patient data and returns ranked protocol suggestions.
    *   `/graph/...`: Allows for direct querying and exploration of the graph data (e.g., finding all evidence related to a specific target).
    *   `/analytics`: Provides access to aggregated data and insights from the graph, such as trends in protocol efficacy or gaps in evidence.

### 4.5 Front-End
The primary user interface for clinicians to interact with APGE is the **React + Tailwind TMS Protocol Tool**. This web-based application, built using Vite, allows clinicians to:
    *   Input patient-specific information.
    *   Receive and review APGE's protocol recommendations.
    *   Explore the underlying evidence supporting each recommendation.
    *   (Future) Provide feedback on protocol effectiveness, closing the loop.

### 4.6 DevOps
To ensure robust development, deployment, and maintenance, APGE utilizes modern DevOps practices:
    *   **Containerization:** Services are containerized using **Docker Compose** for consistent environments and simplified deployment.
    *   **Continuous Integration (CI):** **GitHub Actions** are employed for automated testing, linting, and build processes upon code commits.
    *   **Automated Literature Monitoring:** A scheduled process (e.g., weekly) is planned to scrape relevant literature sources, perform a `diff` against existing evidence, and automatically generate a Pull Request (PR) for review and potential inclusion of new findings into the graph.

### Data Flow Diagram
[Insert Architecture Diagram Here: Illustrating data flow from literature/RWD → ETL → Neo4j Graph → Recommendation Engine → API → Clinician UI → Feedback Loop to Graph]

## 5. Algorithms & Methodology
The APGE leverages several interconnected algorithms and methodologies to transform raw data into actionable, personalized TMS protocol recommendations.

### 5.1 Evidence Rating Model
To systematically evaluate the strength of scientific findings, APGE employs an **Evidence Rating Model**. This model adapts established frameworks, such as the GRADE (Grading of Recommendations, Assessment, Development and Evaluations) methodology, into a numeric scale. For example:
    *   **Level A (High Certainty):** Evidence from well-conducted meta-analyses or multiple large randomized controlled trials (RCTs) with consistent results. Corresponds to a numeric weight, e.g., **1.0**.
    *   **Level B (Moderate Certainty):** Evidence from smaller RCTs, well-designed non-randomized studies, or meta-analyses with some heterogeneity. Corresponds to a numeric weight, e.g., **0.7**.
    *   **Level C (Low Certainty):** Evidence from observational studies, case series, or RCTs with significant limitations. Corresponds to a numeric weight, e.g., **0.4**.
    *   **Level E (Emerging/Expert Opinion):** Evidence from preclinical studies, expert consensus, or case reports, indicating potential but not yet robustly validated findings. Corresponds to a numeric weight, e.g., **0.2**.
This numeric `evidence_weight` is a key input into the recommendation engine's scoring algorithm, ensuring that protocols supported by stronger evidence are prioritized.

### 5.2 Graph Traversal for Protocol Identification
Once patient-specific information (e.g., diagnosis, primary symptoms) is provided, APGE utilizes **graph traversal algorithms** to identify potential treatment pathways within its Neo4j knowledge graph. A typical query pattern involves finding paths such as:
`(Diagnosis)-[:HAS_SYMPTOM]->(Symptom)-[:TARGETED_BY]->(Target)-[:USUALLY_TREATED_WITH]->(StimParams)`

This query structure allows APGE to explore connections from a patient's diagnosed condition and specific symptoms to relevant neuroanatomical targets, and subsequently to the stimulation parameters commonly used or evidenced to be effective for those targets in that clinical context. While "shortest path" can be a component, the system often employs more complex traversals that might consider path weights (e.g., evidence strength of relationships) or multiple alternative paths.

*[Insert Sample Cypher Query Here]*
```cypher
// Example: Find stimulation parameters for 'Anhedonia' in 'MDD'
MATCH (diag:Diagnosis {name: 'Major Depressive Disorder'})-[:HAS_SYMPTOM]->(symp:Symptom {name: 'Anhedonia'}),
      (symp)-[:TARGETED_BY]->(target:Target),
      (target)-[uts:USUALLY_TREATED_WITH]->(params:StimParams),
      (uts)-[:HAS_EVIDENCE]->(ev:Evidence)
RETURN diag.name, symp.name, target.name, params, ev.rating, ev.source
ORDER BY ev.rating DESC
LIMIT 10
```
*(The above is a simplified conceptual example; actual queries may be more complex)*

### 5.3 Multi-criteria Ranking
After identifying potential protocols via graph traversal, APGE employs a **multi-criteria ranking algorithm** to score and order them. The core formula for a protocol's score is a weighted sum:

`score = w₁ * evidence_strength + w₂ * patient_similarity - w₃ * risk_factor`

Where:
    *   `evidence_strength`: Derived from the Evidence Rating Model for the protocol's components.
    *   `patient_similarity`: A measure of how closely the current patient's phenotypic profile matches patient groups for whom the protocol was effective (potentially derived from embeddings or cohort data).
    *   `risk_factor`: A penalty applied based on patient-specific contraindications, comorbidities, age, or other risk-associated variables (e.g., seizure threshold).
    *   `w₁, w₂, w₃`: These are hyperparameters representing the relative importance of each component in the overall score. These weights are not static; they are **tuned and optimized using retrospective registry data** (target dataset n ≈ 2,000) to maximize predictive accuracy for positive treatment outcomes.

### 5.4 Adaptive Loop (Future Development)
Looking ahead, APGE is designed to incorporate an **adaptive loop**, particularly leveraging real-time biomarkers from TMS-fNIRS. The envisioned mechanism is:
1.  **Initial Stimulation & Monitoring:** During the initial phase of a TMS session (e.g., the first 600 pulses), concurrent fNIRS would measure the hemodynamic response (e.g., change in oxygenated hemoglobin, Δ[HbO]) in the targeted cortical region and connected areas.
2.  **Biomarker Feedback:** This immediate neurophysiological feedback (Δ[HbO] signature) serves as a direct indicator of cortical engagement and reactivity.
3.  **Bayesian Update:** The biomarker data will feed into a **Bayesian updating mechanism**. This allows the system to refine its model of the patient's individual response characteristics by comparing the observed response to expected responses based on the graph data.
4.  **Parameter Modulation:** Based on this updated understanding, APGE could then suggest or (in a fully closed-loop system) automatically implement modulations to the pulse-train parameters for the remainder of the session or for subsequent sessions. This could involve adjusting intensity, frequency, or even fine-tuning the target if the initial response is suboptimal.
This adaptive capability aims to create a truly personalized treatment that dynamically adjusts to the patient's unique neurophysiology, moving beyond static protocols.

## 6. Validation Plan
The validation of APGE will proceed through a multi-phase approach, systematically evaluating its technical performance, clinical utility, and impact on patient outcomes.

| Phase   | Milestone                                     | Key Metrics                                         | Timeline Indication |
|---------|-----------------------------------------------|-----------------------------------------------------|---------------------|
| **0 (Current)** | Internal Unit & Integration Testing         | 100% pass rate for all core module unit tests on synthetic patient data. Verification of data integrity and algorithmic logic. | Ongoing             |
| **1**       | Retrospective Chart Review                    | Analysis of n=500 patient charts from 3 clinical centers. **Primary Metric:** Area Under the Curve (AUC) > 0.75 for APGE-suggested protocols predicting treatment response compared to standard guideline-based care. | Q4 2025             |
| **2**       | Prospective Pilot Study                       | Single-arm, open-label trial with n=40 patients with Major Depressive Disorder (MDD). **Primary Metric:** ≥ 50% treatment response rate (e.g., ≥50% reduction in HAM-D/MADRS score) at week 4 of APGE-guided TMS. | Q1-Q2 2026          |
| **3**       | Multi-Site Randomized Controlled Trial (RCT)  | RCT involving n=200 patients with MDD & PTSD across multiple clinical sites. Comparison of APGE-guided TMS vs. treatment-as-usual (guideline-based TMS). **Primary Metric:** Statistically significant improvement in response rates (+12 percentage points difference) with p < 0.05 for APGE arm. | Commencing 2027     |

### Safety Endpoints
Across all prospective clinical validation phases (Phase 2 and 3), safety will be rigorously monitored. The primary safety endpoint is maintaining a seizure rate of **≤ 0.1%**, consistent with established safety profiles for TMS. All adverse events will be systematically recorded and reported according to regulatory requirements.

## 7. Business & Deployment Model
* SaaS licensing to TMS clinics (per-seat or per-treatment).
* OEM partnerships – embed into coil manufacturers’ planning software.
* Data network effects – de-identified outcomes feed model; clinics opt-in for reduced fee.
* Initial TAM: ~2 500 US clinics × $6 k annual license ≈ $15 M.

## 8. Regulatory & Ethics
* FDA CDS (Clinical Decision Support) guidance 2022 – APGE qualifies as non-device CDS if final decision left to clinician; roadmap to 510(k) if adaptive closed-loop controls stimulation automatically.
* HIPAA / GDPR – architecture stores PHI only in hashed form; graph holds abstractions.
* Bias mitigation – track differential accuracy across gender / ethnicity; model fairness audits each release.

## 9. Roadmap

| Quarter   | Deliverable                                         |
|-----------|-----------------------------------------------------|
| Q3 2025   | MVP API + clinician dashboard; pilot data ingestion |
| Q4 2025   | Retrospective validation complete; seed round close   |
| Q1 2026   | Prospective pilot, adaptive algorithm v1           |
| Q3 2026   | Closed-loop TMS-fNIRS integration prototype         |
| 2027      | Multi-site RCT, FDA submission (de novo or 510(k)) |

## 10. Team & Advisors
* Levi Solomon – Co-founder, Neuropsychiatry & fNIRS research.
* Jules – Full-stack / graph systems engineer.
* Clinical advisors – Dr. X (Stanford SAINT), Dr. Y (Harvard McLean).
* Scientific advisors – Dr. Z (Neo4j GDS), Dr. A (TMS-fNIRS pioneer).

## 11. Budget & Financing

| Use of Funds (18 mo)        | Amount    |
|-----------------------------|-----------|
| Engineering (4 FTE)         | $720 k    |
| Data acquisition & labeling | $180 k    |
| Pilot trial ops             | $250 k    |
| Regulatory & legal          | $100 k    |
| Overhead & cloud            | $75 k     |
| Total                       | $1.325 M  |

Seed ask: $1.5 M convertible note.

## 12. Risks & Mitigations
* Data heterogeneity – standardize via common data model; use federated learning.
* Clinical uptake – partner with early-adopter clinics, publish pilot outcomes.
* Regulatory drift – retain expert counsel; design modular CDS to downgrade autonomy if needed.
* Competition – patent provisional on graph-based adaptive TMS dosing; continuous evidence updates as moat.

## 13. Conclusion

Summarize the unique value of a graph-driven, evidence-weighted engine that closes the loop between literature, clinic, and neurophysiology—positioning APGE as the missing layer between raw hardware and truly personalized brain stimulation.

## Next Steps for Drafting
1. Assign owners for each section (e.g., Jules → Architecture & Algorithms; Levi → Clinical Need & Validation).
2. Create a shared Google Doc or Markdown repo; paste this outline as headings.
3. Insert figures/tables: architecture diagram, sample Cypher query, pilot results mock-up.
4. Ruthlessly prune jargon depending on audience.
