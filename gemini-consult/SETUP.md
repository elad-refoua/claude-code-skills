# Gemini Consult Setup

## Prerequisites

- Node.js 18+
- Google AI Studio API key

## Installation

```bash
cd ~/.claude/skills/gemini-consult/scripts
npm install
```

## API Key

1. Get API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Create `.env` file:
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
```

Or reuse from nano-banana-poster:
```bash
cp ~/.claude/skills/nano-banana-poster/scripts/.env .
```

## Verify

```bash
npx tsx consult.ts "Test" --text "Hello world"
```
