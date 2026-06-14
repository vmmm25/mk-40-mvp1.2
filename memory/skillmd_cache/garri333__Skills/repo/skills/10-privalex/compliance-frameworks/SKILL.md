---
name: compliance-frameworks
description: Technical knowledge base on compliance frameworks PrivaLex works with (ISO 27001, NIS2, GDPR, DORA, ENS, ISO 42001, ISO 27701). Use for technical accuracy in content generation.
---

# Compliance Frameworks Knowledge Base

Reference for technical accuracy when writing about compliance and certification.

## ISO/IEC 27001:2022

### What It Is
International standard for Information Security Management Systems (ISMS / SGSI). The gold standard for demonstrating security posture to clients, regulators, and partners.

### Key Structure
- **Clauses 4-10:** Management system requirements (context, leadership, planning, support, operation, evaluation, improvement)
- **Annex A:** 93 controls organized in 4 themes:
  - A.5: Organizational controls (37 controls)
  - A.6: People controls (8 controls)
  - A.7: Physical controls (14 controls)
  - A.8: Technological controls (34 controls)

### Critical Clauses to Reference
- **Clause 4.3:** Scope of the ISMS
- **Clause 6.1.2:** Risk assessment process
- **Clause 6.1.3:** Risk treatment
- **Clause 7.2:** Competence (training requirement)
- **Clause 7.3:** Awareness (staff must know the security policy)
- **Clause 7.5:** Documented information
- **Clause 8.2:** Risk assessment execution
- **Clause 9.2:** Internal audit
- **Clause 10.1:** Nonconformity and corrective action

### Key Documents
- **SGSI (ISMS):** The management system itself
- **SoA (Statement of Applicability / Declaración de Aplicabilidad):** Which Annex A controls apply and why
- **Risk Assessment:** Methodology + results
- **Risk Treatment Plan:** How risks are addressed
- **Internal Audit Report:** Evidence of self-assessment
- **Management Review:** Leadership involvement evidence

### Certification Process
1. Gap analysis
2. ISMS design and implementation
3. Documentation
4. Staff training and awareness
5. Internal audit
6. Management review
7. Stage 1 audit (documentation review by certification body)
8. Stage 2 audit (practical assessment by certification body)
9. Certification (valid 3 years)
10. Annual surveillance audits

### Certification Bodies (Spain/EU)
- Bureau Veritas
- AENOR
- BSI (British Standards Institution)
- TÜV
- DNV
- SGS

---

## RGPD / GDPR

### What It Is
EU General Data Protection Regulation. Mandatory for any organization processing personal data of EU residents.

### Key Principles (Article 5)
1. Lawfulness, fairness, transparency
2. Purpose limitation
3. Data minimization
4. Accuracy
5. Storage limitation
6. Integrity and confidentiality
7. Accountability

### Key Obligations
- **Data Protection Officer (DPO):** Required for public bodies, large-scale monitoring, or special category data processing
- **DPIA (Data Protection Impact Assessment):** Required for high-risk processing
- **Records of Processing Activities (ROPA):** Mandatory documentation
- **Data Breach Notification:** 72 hours to supervisory authority
- **Data Subject Rights:** Access, rectification, erasure, portability, objection, restriction

### Spanish Implementation: LOPDGDD
- Ley Orgánica 3/2018 de Protección de Datos Personales y garantía de derechos digitales
- Adds specific provisions for Spain (digital rights, minors, etc.)
- Supervisory Authority: AEPD (Agencia Española de Protección de Datos)

---

## NIS2 Directive

### What It Is
EU directive on Network and Information Security (Directive 2022/2555). Strengthens cybersecurity obligations across critical sectors.

### Effective Date
- In force since January 2023
- National transposition deadline: October 2024
- Practical enforcement: 2025 onwards

### Who Must Comply
- **Essential entities:** Energy, transport, banking, health, water, digital infrastructure, public administration, space
- **Important entities:** Postal services, waste management, chemicals, food, manufacturing, digital providers, research

### Key Requirements
- Cybersecurity risk management measures
- Incident reporting (24h early warning, 72h full notification)
- Supply chain security
- Business continuity
- **Staff training** (including senior management)
- Governance and accountability at board level

### Penalties
- Essential entities: up to EUR 10M or 2% of global turnover
- Important entities: up to EUR 7M or 1.4% of global turnover

---

## DORA (Digital Operational Resilience Act)

### What It Is
EU regulation for digital operational resilience in the financial sector (Regulation 2022/2554).

### Effective Date
- Applicable from January 17, 2025

### Who Must Comply
- Banks, insurance companies, investment firms
- Payment institutions, e-money institutions
- Crypto-asset service providers
- ICT third-party service providers to financial entities

### Key Pillars
1. ICT risk management
2. ICT incident reporting
3. Digital operational resilience testing
4. ICT third-party risk management
5. Information sharing

---

## ENS (Esquema Nacional de Seguridad)

### What It Is
Spanish National Security Framework (Real Decreto 311/2022). Mandatory for Spanish public administration and their technology providers.

### Levels
- **Básico:** For systems handling low-impact information
- **Medio:** For systems handling medium-impact information
- **Alto:** For systems handling high-impact information

### Who Must Comply
- Spanish public administration entities
- Private companies providing technology services to public administration
- Companies processing classified or public-sector data

### Relationship with ISO 27001
ENS shares many controls with ISO 27001, making dual certification efficient. PrivaLex specializes in implementing both simultaneously.

---

## ISO/IEC 42001:2023

### What It Is
International standard for AI Management Systems (AIMS). Governs responsible development, deployment, and use of artificial intelligence.

### Key Difference from ISO 27001
- ISO 27001: Protects information security (data, systems)
- ISO 42001: Governs AI decisions (ethics, transparency, bias, accountability)

### Key Areas
- Ethical alignment and AI principles
- Transparency and explainability
- Human oversight
- Bias mitigation
- Data quality and labeling
- Autonomy boundaries

### Relationship with EU AI Act
ISO 42001 provides a structured framework to meet many requirements of the AI Act, particularly for high-risk AI systems.

---

## ISO/IEC 27701:2025

### What It Is
Privacy extension to ISO 27001. Establishes requirements for Privacy Information Management Systems (PIMS / SGPI).

### Key Updates in 2025 Version
- Aligned with ISO 27001:2022 structure
- Updated privacy controls mapping
- Stronger documentation and accountability requirements
- Better integration with GDPR accountability principle
- Cross-references with ISO 27001:2022 Annex A

### Relationship with GDPR
ISO 27701 provides the management system framework to operationalize GDPR requirements. Certification demonstrates "appropriate technical and organizational measures" (Art. 32 GDPR).

---

## Framework Relationships

```
ISO 27001 (Security Foundation)
├── ISO 27701 (Privacy Extension)
├── ISO 42001 (AI Governance)
├── ENS (Spanish Public Sector)
├── SOC 2 (US Market Trust)
└── Supports compliance with:
    ├── RGPD/GDPR
    ├── NIS2
    ├── DORA
    └── AI Act
```

## Common Misconceptions to Address in Content

| Misconception | Reality |
|---------------|---------|
| "ISO 27001 is just documentation" | It requires implemented, functioning controls verified by auditors |
| "Small companies don't need ISO 27001" | Enterprise clients increasingly require it from suppliers of any size |
| "GDPR compliance = ISO 27001" | They overlap but serve different purposes; ISO 27001 covers broader security |
| "Once certified, you're done" | 3-year cycle with annual surveillance audits + continuous improvement |
| "NIS2 only applies to large companies" | Important entities include medium-sized companies in covered sectors |
| "You can self-certify ISO 27001" | Must be audited by an accredited certification body |
