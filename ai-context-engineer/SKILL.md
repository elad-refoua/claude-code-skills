---
name: ai-context-engineer
description: >
  Structure any AI interaction using the Context/Constraints/Goal framework.
  The super-principle: it's not the prompt that matters — it's the context you give the AI.
  Provides templates and checklists for academic, clinical, and technical tasks.
skills:
  - ai-thinking-framework
triggers:
  - context engineering
  - structure my prompt
  - הנדסת הקשר
  - context constraints goal
  - prepare context for AI
  - build context
---

# Context Engineering

**The key is not the prompt itself — the key is the context you give the AI.**

## The Three Pillars

### 1. Context — What does the AI need to know?

| Question | Why it matters |
|----------|----------------|
| What's the domain? | Sets the vocabulary and assumptions |
| What's the central question? | Focuses the response |
| What's the theoretical background? | Prevents generic answers |
| What methodology is used? | Constrains the kind of answer |
| What population/audience? | Adapts tone, complexity, examples |
| What socio-cultural context? | Prevents culturally inappropriate output |

### 2. Constraints — What are the boundaries?

| Question | Why it matters |
|----------|----------------|
| Methodological limits? | Keeps recommendations feasible |
| Source types allowed? | Peer-reviewed only? Gray literature? |
| Ethical boundaries? | What the AI must NOT do |
| Date/geographic range? | Narrows search scope |
| Languages or disciplines? | Prevents cross-domain confusion |
| Word count or format limits? | Matches practical requirements |

### 3. Goal — What's the final product?

| Question | Why it matters |
|----------|----------------|
| What format? | Literature review? Code? Presentation? |
| Who's the audience? | Determines depth and tone |
| What patterns or insights? | Tells AI what to look for |
| How will this be used? | Shapes the output structure |

---

## Context Engineering Checklist

Before sending any important prompt, verify:

- [ ] **Domain stated** — The AI knows what field you're in
- [ ] **Central question clear** — Not vague, not too broad
- [ ] **Background provided** — Key theories, prior findings, or existing code
- [ ] **Constraints explicit** — What the AI should NOT do or assume
- [ ] **Output format defined** — Exact deliverable described
- [ ] **Audience specified** — Who will read/use this
- [ ] **Materials attached** — Relevant docs, data samples, or references

---

## Domain Templates

### Academic Research

```
CONTEXT: I'm a [role] in [field]. My research question is [X].
The theoretical framework is [Y]. Population: [Z].
Prior findings show [summary].

CONSTRAINTS: Focus on [methodology type]. Only peer-reviewed
sources from [year range]. Language: [Hebrew/English].
Do not assume [specific assumption].

GOAL: Produce [deliverable] for [audience/journal].
Format: [APA/specific structure]. Length: [word count].
```

### Clinical Work

```
CONTEXT: Clinical setting: [type]. Patient population: [demographics].
Therapeutic approach: [model/framework].
Current challenge: [what needs to be addressed].

CONSTRAINTS: Evidence-based only. No diagnostic conclusions.
Ethical boundary: [specific limit]. Cultural context: [Israeli/other].

GOAL: [What you need — session plan, psychoeducation material,
assessment summary]. For: [clinician use / patient-facing].
```

### Technical / Coding

```
CONTEXT: Project: [description]. Tech stack: [languages/frameworks].
Current code does [X]. I need to [change/add Y].
Relevant files: [paths].

CONSTRAINTS: Must work with [existing system]. No new dependencies
unless justified. Follow [coding style/convention].
Performance requirement: [if applicable].

GOAL: Working code for [specific function]. Include: [tests/comments/docs].
Output format: [complete file / diff / explanation].
```

### Content Creation

```
CONTEXT: Topic: [subject]. My expertise level: [background].
Existing content: [what I already have].
Target platform: [blog/presentation/social media].

CONSTRAINTS: Tone: [formal/conversational/academic].
Length: [word count]. Language: [Hebrew/English].
Must include: [required elements]. Must avoid: [prohibited content].

GOAL: [Draft/outline/final version] for [audience].
Key message: [what the reader should take away].
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No context — "Write about anxiety" | Add domain, population, purpose |
| No constraints — "Analyze this data" | Add method, scope, what NOT to assume |
| No goal — "Help me with my paper" | Specify which section, format, audience |
| Too much context, no structure | Use the 3-pillar template |
| Context in one blob of text | Separate Context / Constraints / Goal clearly |
| Assuming AI "knows" your project | Always re-state key facts at conversation start |

---

## When to Use This Skill

- Before any complex AI interaction (research, writing, analysis)
- When AI gives vague or off-target responses (usually a context problem)
- When preparing prompts for others (workshops, teaching)
- When building AI systems (the 3 pillars map to system prompts)
