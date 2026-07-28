---
name: claude-cli-subprocess
description: Call the Claude Code CLI (claude -p) as a subprocess from Node.js, Python, or shell scripts to use Anthropic models for free LLM tasks inside automated pipelines. Replaces paid SDK calls in places that don't need streaming. Includes input-via-stdin pattern, output cleanup (strip wrapping quotes, role prefixes, code blocks), model selection (haiku for speed, opus for quality), and fallback handling.
---

# Calling `claude -p` as a Subprocess

## When to use

Your automated pipeline (a Node.js Playwright recorder, a Python data
processing script, a bash CI job) needs an LLM call inline. Examples:
- Generate the next chat message based on history (recorder bots)
- Classify a batch of items
- Summarize logs
- Score outputs (LLM-as-judge)
- Translate text inline

Use `claude -p` as a subprocess instead of calling the Anthropic SDK. This approach
uses **Claude Code agents over paid API calls** — `claude -p` is "free" under the
Claude Code subscription, replacing costly SDK calls in automated pipelines.

Triggers:
- "free LLM call in my script"
- "generate text inside a recorder"
- "use claude inside this Python script"
- "LLM as a subprocess"
- "claude -p call from node"

## CLI surface

```bash
claude -p [--model haiku|sonnet|opus]
```

- `-p` = print mode (no interactive REPL, single round trip)
- Input via STDIN (preferred) or as the final positional argument
- Output goes to STDOUT, no chrome/prefixes by default
- Exit code 0 on success, non-zero on auth/network/model errors

Test it works:
```bash
echo "Reply with just the word OK." | claude -p --model haiku
# → OK
```

## Node.js pattern (Playwright recorders, MCP servers)

```js
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

function callClaude(prompt, model = 'haiku') {
  // Write prompt to temp file — avoids shell-escape hell
  const tmp = path.join(os.tmpdir(), `claude_prompt_${Date.now()}.txt`);
  fs.writeFileSync(tmp, prompt, 'utf8');

  const res = spawnSync('claude', ['-p', '--model', model], {
    input: fs.readFileSync(tmp),
    encoding: 'utf8',
    timeout: 60000,
    shell: true   // important on Windows for the `claude` command
  });
  fs.unlinkSync(tmp);

  if (res.status !== 0) {
    throw new Error(`claude -p failed (${res.status}): ${res.stderr || res.stdout}`);
  }

  let out = (res.stdout || '').trim();
  return cleanOutput(out);
}

function cleanOutput(s) {
  // Strip wrapping quotes (occasional Claude habit)
  s = s.replace(/^["'""'']+|["'""'']+$/g, '').trim();
  // Strip "Mom:" / "Assistant:" / similar prefixes
  s = s.replace(/^(Mom|Parent|Mother|Assistant|Output)[:：]\s*/i, '').trim();
  // Take only first non-empty paragraph (avoids commentary after main reply)
  const para = s.split(/\n\n+/)[0].trim();
  if (para) s = para;
  return s;
}
```

## Python pattern

```python
import subprocess
import os
import tempfile

def call_claude(prompt: str, model: str = 'haiku', timeout: int = 60) -> str:
    """Run claude -p and return cleaned output."""
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', suffix='.txt') as f:
        f.write(prompt)
        tmp_path = f.name
    try:
        with open(tmp_path, 'r', encoding='utf-8') as f:
            res = subprocess.run(
                ['claude', '-p', '--model', model],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )
    finally:
        os.unlink(tmp_path)
    if res.returncode != 0:
        raise RuntimeError(f'claude -p failed ({res.returncode}): {res.stderr or res.stdout}')
    return _clean(res.stdout.strip())


def _clean(s: str) -> str:
    import re
    s = re.sub(r'^["\'""'']+|["\'""'']+$', '', s).strip()
    s = re.sub(r'^(Mom|Parent|Mother|Assistant|Output)[:：]\s*', '', s, flags=re.I).strip()
    first_para = s.split('\n\n')[0].strip()
    return first_para if first_para else s
```

## Iron rules for the prompt

1. **Be explicit about language.** Claude defaults to the language of the
   surrounding context. If you need English specifically, say "Respond ONLY in
   ENGLISH" in the prompt — otherwise Hebrew prompts may yield Hebrew output
   even when undesired.

2. **Demand a single output, no commentary.** End the prompt with:
   "Output ONLY the [thing] itself — no commentary, no quotation marks, no
   labels. Just the [thing]."

3. **Include all context.** Subprocess calls don't have memory between
   invocations. Pass full conversation history each time.

4. **Use `--model haiku` for fast pipelines.** Latency: ~3-8s per call vs
   ~10-25s for Sonnet/Opus. Quality is usually sufficient for short tactical
   outputs. Use `--model opus` only when you need it.

## Performance notes

| Model | Latency per call | Use case |
|-------|------------------|----------|
| haiku | 3-8s | Recorder bots, batch classification, short tactical generation |
| sonnet | 8-15s | Quality-sensitive single-shot generation |
| opus | 15-30s | When you need the best, infrequent calls |

A 20-turn recorder using haiku adds ~120s total LLM latency. Acceptable for
demo recordings. For a 100-item batch classification, parallelize via thread
pool (5-10 concurrent calls without hitting limits).

## Gotchas

- **Windows shell escaping**: passing the prompt as an argument with `"..."`
  loses newlines, breaks on quotes inside the prompt. ALWAYS use stdin with
  temp file as shown above.
- **`shell: true` on Node.js Windows**: `claude` is a `.cmd` shim; `shell: false`
  often fails to find it. Setting `shell: true` resolves it via PATH.
- **Default model**: omitting `--model` uses the user's default (likely Sonnet
  or Opus). Always specify explicitly in scripts so behavior doesn't drift
  with user config changes.
- **Streaming vs print**: `-p` is single-shot non-streaming. If you need
  streaming (typewriter effect), use `claude` without `-p` and parse output
  events — but that's much more complex and rarely needed in pipelines.
- **Rate limits**: Claude Code subscription has fair-use limits. ~100 calls/min
  is usually safe; sustained high-volume work may throttle. Add `time.sleep(0.5)`
  between batched calls if you hit issues.

## Example: adaptive dialogue message generator (production use)

This pattern is useful for simulation recorders and dialogue bots. It
generates each character reply based on (history + intent + style + profile):

```js
function generateCharacterMessage(history, turnDef, profile) {
  const historyText = history.length === 0
    ? '(this is the first message)'
    : history.map(h => `AGENT: ${h.agent}\nBOT: ${h.bot}`).join('\n\n');

  const prompt = `You are roleplaying a character. Respond ONLY in ENGLISH.

YOUR PROFILE: ${profile.label}.
${profile.description}

Turn intent: ${turnDef.intent}
Turn style: ${turnDef.style}
Example phrasing (do not copy): ${turnDef.example}

Conversation so far:
${historyText}

Output ONLY the next character message — no commentary, no quotes, no labels.`;

  return callClaude(prompt, 'haiku');
}
```

This pattern is repeatable across simulation recorders, LLM-as-judge
pipelines, content augmentation, and anywhere else you need adaptive,
context-aware text generation without paid API calls.
