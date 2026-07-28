---
name: git-quick
description: Quick GitHub operations - create repos, push code, setup authentication. Use when user wants to upload to GitHub, create a repo, or setup git.
---

# Git Quick - Fast GitHub Operations

This skill provides fast, no-browser GitHub operations using the `gh` CLI.

## Available Commands

When user invokes this skill, ask what they want to do:

1. **Setup** - First-time GitHub authentication
2. **New Repo** - Create a new repo and push current folder
3. **Push** - Push changes to existing repo
4. **Status** - Check git and GitHub status

## Instructions for Each Command

### 1. Setup (First-time only)

Check if already authenticated:
```bash
"/c/Program Files/GitHub CLI/gh.exe" auth status
```

If not authenticated, run:
```bash
"/c/Program Files/GitHub CLI/gh.exe" auth login --web --git-protocol https
```

Then setup git credentials:
```bash
"/c/Program Files/GitHub CLI/gh.exe" auth setup-git
git config --global user.name "USER_NAME"
git config --global user.email "USER_EMAIL"
```

### 2. New Repo (Most common)

For creating a new repo from current folder:

```bash
# Initialize if needed
git init

# Add all files
git add -A

# Commit
git commit -m "COMMIT_MESSAGE"

# Create repo and push (ask user for repo name and if public/private)
"/c/Program Files/GitHub CLI/gh.exe" repo create REPO_NAME --public --source . --push
```

Ask user:
- Repo name (suggest based on folder name)
- Public or private?
- Commit message (suggest based on content)

### 3. Push (Update existing repo)

```bash
git add -A
git commit -m "COMMIT_MESSAGE"
git push origin main || git push origin master
```

### 4. Status

```bash
"/c/Program Files/GitHub CLI/gh.exe" auth status
git status
git remote -v
```

## Important Notes

- Always use full path for gh: `"/c/Program Files/GitHub CLI/gh.exe"`
- If gh not found, tell user to run: `winget install GitHub.cli`
- For commit messages, use descriptive messages based on changes
- Always check `git status` before committing
