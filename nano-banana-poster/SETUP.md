# Nano Banana Poster - Setup Guide

## Prerequisites

- Google Cloud account (for Gemini API)
- Node.js installed

## 1. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key" → "Create API key"
4. Choose a project or create new one

## 2. Link Billing Account (IMPORTANT!)

The API key's project **must be linked to a billing account** for the API to work:

1. Go to [Google Cloud Console - Billing](https://console.cloud.google.com/billing/projects)
2. Find your project in "Your projects" tab
3. If it shows "Billing is disabled", click the Actions menu (⋮) → "Change billing"
4. Select your billing account

**Note:** Free tier provides ~50 images/day with a billing account linked.

## 3. Configure Credentials

Create `.env` in `scripts/` folder:

```bash
GEMINI_API_KEY=your_api_key_here
```

## 4. Install Dependencies

```bash
cd scripts/
npm install
```

## 5. Test

```bash
# Basic generation (use tsx, not ts-node)
npx tsx generate_poster.ts "A beautiful sunset over mountains"
```

Output will be saved as `poster_0.jpg` in current directory.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 error | Check API key |
| 429 error (quota) | Link billing account to project, or wait for quota reset |
| Rate limited | Wait a few minutes |
| Image not generated | Check prompt for safety filters |
| ESM module error | Use `npx tsx` instead of `npx ts-node` |

## Notes

- **Model:** `gemini-3-pro-image-preview` (Nano Banana Pro)
- Free tier has ~50 images/day limit
- Some prompts may be filtered for safety
- Images are 1024px on longest edge
- Billing account must be linked even for free tier
