---
name: privacy-hipaa
description: |
  HIPAA compliance requirements, checklists, and GCP infrastructure setup.
  Use when implementing or reviewing HIPAA compliance for health data processing,
  or setting up HIPAA-compliant cloud infrastructure (Vertex AI, GCP, Vercel).
  Triggers: "HIPAA compliance", "hipaa setup", "vertex ai setup", "gcp hipaa"
user-invocable: true
---

# HIPAA Compliance Requirements

## Overview

HIPAA (Health Insurance Portability and Accountability Act) applies to:
- **Covered Entities**: Healthcare providers, health plans, clearinghouses
- **Business Associates**: Any entity handling PHI on behalf of covered entities

## Key Definitions

| Term | Definition |
|------|------------|
| **PHI** | Protected Health Information - individually identifiable health info |
| **ePHI** | Electronic PHI |
| **BAA** | Business Associate Agreement |
| **Minimum Necessary** | Use only the minimum PHI needed |

## The Three Safeguards

### 1. Administrative Safeguards (§164.308)

| Requirement | Implementation |
|-------------|----------------|
| Security Officer | Designate person responsible for security |
| Risk Analysis | Conduct regular security risk assessments |
| Workforce Training | Train all staff on HIPAA policies |
| Access Management | Implement role-based access controls |
| Incident Response | Establish breach response procedures |
| Contingency Plan | Backup, disaster recovery, emergency mode |
| Evaluation | Periodic security evaluations |
| BAA Contracts | Written agreements with all business associates |

### 2. Physical Safeguards (§164.310)

| Requirement | Implementation |
|-------------|----------------|
| Facility Access | Control physical access to data centers |
| Workstation Use | Policies for workstation security |
| Workstation Security | Physical protections for devices |
| Device Controls | Media disposal, re-use, movement tracking |

### 3. Technical Safeguards (§164.312)

| Requirement | Implementation |
|-------------|----------------|
| Access Control | Unique user IDs, emergency access, auto-logoff |
| Audit Controls | Record and examine system activity |
| Integrity Controls | Protect ePHI from improper alteration |
| Authentication | Verify person/entity identity |
| Transmission Security | Encryption for data in transit |

## Breach Notification Rule (§164.400-414)

### Timeline
- **To Individuals**: Without unreasonable delay, no later than **60 days**
- **To HHS**:
  - <500 individuals: Annual log
  - ≥500 individuals: Within 60 days
- **To Media**: If ≥500 individuals in a state

### Required Content
1. Description of what happened
2. Types of information involved
3. Steps individuals should take
4. What entity is doing to investigate/mitigate
5. Contact information

## BAA Requirements

A Business Associate Agreement must include:
- [ ] Permitted uses and disclosures
- [ ] Safeguards requirement
- [ ] Subcontractor requirements
- [ ] Breach notification obligations
- [ ] Return/destruction of PHI at termination
- [ ] HHS audit rights

## Cloud Provider Compliance

### Google Cloud (Vertex AI)
1. Sign Google Workspace HIPAA BAA
2. Enable GCP Platform Sharing
3. Use Vertex AI (covered under BAA)
4. Ensure no data retention by AI models

### Vercel/Other Providers
- Obtain signed BAA or DPA
- Verify HIPAA compliance statement
- Document in security architecture

## GCP HIPAA Infrastructure Setup Guide

Step-by-step guide for setting up HIPAA-compliant AI infrastructure using Google Cloud Vertex AI and Workload Identity Federation.

### Step 1: Assessment

Before starting, confirm:
1. Do you have a Google Workspace account with HIPAA BAA signed?
2. Do you have a Vercel project for deployment?
3. What is your Vercel organization/team slug?
4. What is your Vercel project name?

### Step 2: Enable GCP in Admin Console

- URL: https://admin.google.com
- Path: Apps > Additional Google services > Settings for Google Cloud Platform
- Action: Enable for everyone, allow project creation

### Step 3: Create GCP Project

- URL: https://console.cloud.google.com/projectcreate
- Project name should include "hipaa" for clarity
- Note the Project Number (important for WIF)

### Step 4: Enable Vertex AI API

- URL: APIs & Services > Enable APIs
- Search and enable "Vertex AI API"

### Step 5: Create Service Account

- URL: IAM & Admin > Service Accounts
- Name: `vertex-ai-user` or similar
- Role: Vertex AI User (roles/aiplatform.user)
- DO NOT create keys (WIF is more secure)

### Step 6: Workload Identity Federation

This is the most complex step:

1. **Create Pool:** Name: Vercel, ID: vercel
2. **Add OIDC Provider:**
   - Issuer: https://oidc.vercel.com
   - Audience: https://vercel.com/{VERCEL_ORG}
3. **Configure Attributes:** google.subject = assertion.sub
4. **Grant Access:**
   - Service account impersonation
   - Subject: owner:{VERCEL_ORG}:project:{PROJECT}:environment:production

### Step 7: Vercel Configuration

Set environment variables:
```
GCP_PROJECT_ID
GCP_PROJECT_NUMBER
GCP_WORKLOAD_IDENTITY_POOL_ID
GCP_WORKLOAD_IDENTITY_POOL_PROVIDER_ID
GCP_SERVICE_ACCOUNT_EMAIL
```

### Step 8: Verification

Test the complete setup with a curl command or via the application.

### GCP Troubleshooting

**Organization Policy Errors** — If you encounter `iam.disableServiceAccountKeyCreation`: this is EXPECTED for Workspace accounts with HIPAA BAA. WIF is the solution and is MORE secure. Do not try to disable the policy.

**No Organization Visible** — Common for new GCP users. Project can still be created under "No organization." Organization policies may still apply.

**Security Notes:**
1. NEVER store service account keys in production
2. WIF is the recommended approach for Vercel
3. Always verify the correct account is logged in
4. Document all configuration for records

## Compliance Checklist

### Technical Controls
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Unique user authentication
- [ ] Role-based access control
- [ ] Automatic session timeout
- [ ] Audit logging enabled
- [ ] Backup procedures in place

### Administrative Controls
- [ ] Security officer designated
- [ ] Risk assessment completed
- [ ] Policies documented
- [ ] Staff training conducted
- [ ] Incident response plan exists
- [ ] BAAs with all vendors

### Documentation
- [ ] Security policies
- [ ] Risk assessment report
- [ ] Training records
- [ ] BAA copies
- [ ] Incident response plan
- [ ] Audit logs retained (6 years)

## Common Implementation Patterns

### Consent Collection
```javascript
{
  "granted": true,
  "version": "1.0",
  "timestamp": "ISO8601",
  "purpose": "Treatment/Research/Operations"
}
```

### Audit Log Entry
```javascript
{
  "timestamp": "ISO8601",
  "userId": "hashed_identifier",
  "action": "access|create|update|delete",
  "resource": "PHI_type",
  "outcome": "success|failure",
  "ipAddress": "masked"
}
```

### Minimum Necessary Access
- Use pseudonymization where possible
- Implement field-level access controls
- Log all PHI access
- Review access regularly

## References

- [HHS HIPAA Home](https://www.hhs.gov/hipaa/index.html)
- [Security Rule Guidance](https://www.hhs.gov/hipaa/for-professionals/security/guidance/index.html)
- [Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html)
