---
name: python-windows
description: Python execution on Windows using py launcher. Use when running Python scripts, installing packages, or managing virtual environments on Windows.
allowed-tools: [Bash]
---

# Python on Windows

**CRITICAL**: On Windows systems, always use the `py` launcher instead of `python` or `python3` commands.

## Why Use `py`?

The `python` command on Windows often points to a Microsoft Store stub that doesn't work. The `py` launcher is the reliable way to run Python on Windows.

## Common Commands

### Running Python Scripts
```bash
# Run a Python script
py script.py

# Run with specific Python version
py -3 script.py
py -3.11 script.py
```

### Package Management
```bash
# Install a package
py -m pip install package-name

# Install with user flag
py -m pip install --user package-name

# Upgrade pip
py -m pip install --upgrade pip

# Install from requirements
py -m pip install -r requirements.txt
```

### Virtual Environments
```bash
# Create virtual environment
py -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate
```

### Checking Python
```bash
# Check Python version
py --version

# List all installed Python versions
py --list-paths

# Check pip version
py -m pip --version
```

## Best Practices

1. **Always use `py`** - Never use `python` or `python3` on Windows
2. **Use `-m` flag** - Run modules with `py -m module_name`
3. **Specify versions** - Use `py -3.11` when multiple Python versions are installed
4. **Virtual environments** - Always activate venv on Windows with `venv\Scripts\activate`

## Quick Reference

| Task | Command |
|:-----|:--------|
| Run script | `py script.py` |
| Install package | `py -m pip install pkg` |
| Create venv | `py -m venv venv` |
| Activate venv | `venv\Scripts\activate` |
| Check version | `py --version` |
| List Pythons | `py --list-paths` |
