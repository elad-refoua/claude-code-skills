---
name: skill-maker
description: |
  Create new Claude Code skills from natural language descriptions.

  TRIGGERS: "create skill", "new skill", "make skill", "build skill",
  "I want a skill that", "I need a skill for", "skill for",
  "יצירת סקיל", "סקיל חדש", "תיצור לי סקיל"

  Follows Anthropic's official skill-creator patterns with YAML frontmatter,
  progressive disclosure, and proper trigger descriptions.
---

# Skill Maker

Create skills following official Anthropic patterns.

## Process

### Step 1: Understand
Ask 2-3 clarifying questions MAX:
- What should the skill do? (one sentence)
- When should it trigger? (specific phrases user would say)
- Any specific tools or files needed?

### Step 2: Generate
Create skill folder:
```
~/.claude/skills/[skill-name]/
└── SKILL.md
```

Use Write tool to create the file.

### Step 3: Validate
- name: kebab-case only (e.g., email-helper)
- description: Under 1024 chars
- description MUST include TRIGGERS section
- Body: Under 500 lines

## SKILL.md Template

```yaml
---
name: [kebab-case-name]
description: |
  [What it does - 1 sentence]

  TRIGGERS: [List specific phrases that should activate this skill]
  [Include both English and Hebrew triggers if relevant]
---

# [Skill Name]

## Instructions
[Clear, concise guidance for Claude]

## Examples
[Show expected inputs and outputs]
```

## Naming Rules

- Always kebab-case: `email-helper` not `emailHelper`
- No spaces: `code-review` not `code review`
- Descriptive: `r-analysis` not `ra`

## Response Format

After creating:
```
✅ Skill created: [skill-name]
📁 Location: ~/.claude/skills/[skill-name]/
🎯 Triggers on: [key phrases]

Test it by saying: "[example trigger phrase]"
```

## What NOT to Include

- No README.md
- No CHANGELOG.md
- No extra documentation
- Only SKILL.md (and scripts/references if truly needed)
