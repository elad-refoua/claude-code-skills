---
name: claudeception
description: |
  Extracts reusable knowledge from work sessions into new skills.
  Triggers: /claudeception, "save this as a skill", "what did we learn?",
  or after non-obvious debugging/workarounds.
---

# Claudeception - Skill Extraction System

## When to Extract

Extract when encountering:
- Non-obvious solutions requiring investigation
- Project-specific patterns/conventions
- Tool/API integration knowledge not in docs
- Error resolution (especially misleading errors)
- Workflow optimizations

## Quality Criteria

- **Reusable**: Helps future tasks, not just this one
- **Non-trivial**: Required discovery, not just docs lookup
- **Specific**: Exact trigger conditions and solution
- **Verified**: Actually worked

## Skill Template

```markdown
---
name: descriptive-kebab-case
description: |
  [Precise: (1) use cases, (2) trigger conditions/errors, (3) what it solves]
version: 1.0.0
---

# Skill Name

## Problem
[What this addresses]

## Trigger Conditions
[When to use - exact errors, symptoms, scenarios]

## Solution
[Steps to apply]

## Verification
[How to verify it worked]

## Notes
[Caveats, edge cases]
```

## Save Location

- Project-specific: `.claude/skills/[name]/SKILL.md`
- User-wide: `~/.claude/skills/[name]/SKILL.md`

## Retrospective Mode (/claudeception)

1. Review session for extractable knowledge
2. List candidates with justifications
3. Extract top 1-3 skills
4. Report what was created

## Self-Check After Tasks

Ask: "Did I spend time investigating something non-obvious?"
If yes → extract skill immediately.

## Avoid

- Over-extraction (not every task = skill)
- Vague descriptions
- Unverified solutions
- Documentation duplication
