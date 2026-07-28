---
name: privacy-check
description: |
  Run privacy and data protection compliance checks.
  Routes to the correct framework: HIPAA, GDPR, or Israeli Privacy Law.
  Use when implementing or reviewing privacy compliance for any data processing system.
user-invocable: true
---

# Privacy Compliance Check

## Auto-Detection
Determine which framework applies based on context:
- **Health data / US patients / PHI** → Load `/privacy-hipaa`
- **EU residents / personal data / EU market** → Load `/privacy-gdpr`
- **Israeli users / Israeli organization / חוק הגנת הפרטיות** → Load `/privacy-israeli`
- **Multiple jurisdictions** → Load all relevant frameworks and note overlaps

## If Framework Is Unclear
Ask the user:
1. Where are the data subjects located? (US, EU, Israel, other)
2. Is this health/medical data?
3. Is the organization based in Israel?

Then load the matching skill(s) from `~/.claude/skills/`.

## Multi-Framework Projects
For projects serving multiple jurisdictions (e.g., an Israeli org with potential US/EU users):
- Run Israeli Privacy Law check first (primary jurisdiction)
- Then HIPAA if health data is involved
- Then GDPR if EU users are served
- Produce a unified compliance report noting where requirements overlap
