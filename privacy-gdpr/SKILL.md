---
name: privacy-gdpr
description: |
  GDPR compliance requirements and checklists.
  Use when implementing or reviewing GDPR compliance for EU data subjects.
user-invocable: true
---

# GDPR Compliance Requirements

## Overview

GDPR (General Data Protection Regulation) applies when:
- Processing personal data of **EU residents**
- Organization is **established in EU**, OR
- Organization **offers goods/services to EU**, OR
- Organization **monitors behavior in EU**

## Key Principles (Article 5)

| Principle | Meaning |
|-----------|---------|
| **Lawfulness, Fairness, Transparency** | Legal basis, fair processing, clear communication |
| **Purpose Limitation** | Collect for specified, explicit purposes only |
| **Data Minimization** | Only collect what's necessary |
| **Accuracy** | Keep data accurate and up to date |
| **Storage Limitation** | Don't keep longer than necessary |
| **Integrity & Confidentiality** | Appropriate security measures |
| **Accountability** | Demonstrate compliance |

## Lawful Basis (Article 6)

Must have ONE of these:

| Basis | When to Use |
|-------|-------------|
| **Consent** | Freely given, specific, informed, unambiguous |
| **Contract** | Necessary to fulfill a contract |
| **Legal Obligation** | Required by law |
| **Vital Interests** | Protect someone's life |
| **Public Task** | Official authority or public interest |
| **Legitimate Interests** | Business interest (balance test required) |

### Special Categories (Article 9)
Health data requires **explicit consent** or specific exemptions.

## Consent Requirements (Article 7)

Valid consent must be:
- [ ] **Freely given** - No imbalance of power
- [ ] **Specific** - For defined purposes
- [ ] **Informed** - Clear information provided
- [ ] **Unambiguous** - Clear affirmative action
- [ ] **Withdrawable** - Easy to withdraw as to give
- [ ] **Documented** - Proof of consent retained

### Consent Implementation
```javascript
{
  "granted": true,
  "version": "1.0",
  "timestamp": "2026-02-06T10:00:00Z",
  "purposes": ["service", "research"],
  "withdrawable": true,
  "dataSubjectId": "pseudonymized_id"
}
```

## Data Subject Rights

### Article 15: Right of Access
- Confirm if data is processed
- Access to the data
- Information about processing

### Article 16: Right to Rectification
- Correct inaccurate data
- Complete incomplete data

### Article 17: Right to Erasure ("Right to be Forgotten")
- Delete data when:
  - No longer necessary
  - Consent withdrawn
  - Objection with no override
  - Unlawful processing

### Article 18: Right to Restriction
- Limit processing in certain cases

### Article 20: Right to Data Portability
- Receive data in machine-readable format
- Transmit to another controller

### Article 21: Right to Object
- Object to processing based on legitimate interests
- Object to direct marketing (absolute right)

### Article 22: Automated Decision-Making
- Right not to be subject to solely automated decisions
- Including profiling with legal effects

## Breach Notification (Article 33-34)

### To Supervisory Authority (Article 33)
- **Timeline**: Within **72 hours** of awareness
- **Exception**: Unless unlikely to result in risk

### To Data Subjects (Article 34)
- **When**: High risk to rights and freedoms
- **Timeline**: Without undue delay

### Required Content
1. Nature of breach
2. Categories and number of subjects
3. DPO contact details
4. Likely consequences
5. Measures taken/proposed

## Data Protection Impact Assessment (Article 35)

### Required When
- Systematic evaluation of personal aspects (profiling)
- Large-scale processing of special categories
- Systematic monitoring of public areas
- New technologies with high risk

### DPIA Must Contain
1. Description of processing operations
2. Assessment of necessity and proportionality
3. Assessment of risks to rights and freedoms
4. Measures to address risks

## Data Protection Officer (Article 37-39)

### Required When
- Public authority/body
- Core activities require large-scale monitoring
- Core activities involve special category data at scale

### DPO Responsibilities
- Inform and advise on obligations
- Monitor compliance
- Cooperate with supervisory authority
- Act as contact point

## International Transfers (Chapter 5)

Data can only be transferred outside EU/EEA if:
1. **Adequacy decision** exists (Israel is adequate!)
2. **Appropriate safeguards** (SCCs, BCRs)
3. **Derogations** (explicit consent, contract necessity)

## Technical Requirements Checklist

### Security (Article 32)
- [ ] Pseudonymization
- [ ] Encryption (transit and rest)
- [ ] Confidentiality assurance
- [ ] Integrity assurance
- [ ] Availability assurance
- [ ] Resilience of systems
- [ ] Restore access after incident
- [ ] Regular testing of measures

### Privacy by Design (Article 25)
- [ ] Data minimization by default
- [ ] Purpose limitation built-in
- [ ] Access controls by default
- [ ] Retention limits automated

### Records of Processing (Article 30)
- [ ] Controller name and contact
- [ ] Purposes of processing
- [ ] Categories of data subjects
- [ ] Categories of personal data
- [ ] Recipients/categories of recipients
- [ ] Transfers to third countries
- [ ] Retention periods
- [ ] Security measures description

## Compliance Checklist

### Legal Framework
- [ ] Lawful basis identified for each processing
- [ ] Privacy policy published
- [ ] Consent mechanism (if applicable)
- [ ] Data subject rights procedures

### Technical Measures
- [ ] Encryption implemented
- [ ] Access controls configured
- [ ] Audit logging enabled
- [ ] Breach detection capability
- [ ] Data portability export

### Documentation
- [ ] Records of processing activities
- [ ] DPIA completed (if required)
- [ ] Consent records retained
- [ ] Breach notification procedures
- [ ] DPO appointed (if required)

### Contracts
- [ ] DPA with processors
- [ ] SCCs for international transfers
- [ ] Joint controller agreements (if applicable)

## Penalties (Article 83)

| Violation Level | Maximum Fine |
|-----------------|--------------|
| Lower tier | €10M or 2% global turnover |
| Higher tier | €20M or 4% global turnover |

## Useful Resources

- [GDPR Full Text](https://gdpr.eu/tag/gdpr/)
- [Article 29 Working Party Guidelines](https://ec.europa.eu/newsroom/article29/news-overview.cfm)
- [EDPB Guidelines](https://edpb.europa.eu/our-work-tools/general-guidance_en)
