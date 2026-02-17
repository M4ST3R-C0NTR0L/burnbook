# 🔥 BurnBook

> **The code quality roaster that tells it like it is.**
>
> Your code's honest friend (that no one asked for).

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-coming_soon-orange.svg)](https://pypi.org)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

![BurnBook Demo](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3J6Y3B5eHh4a3R0b3J4eW5qZ3N0eXJ1Z2h0d3J5Z3J5d3J5Z3J5d3J5Z3J5d3J5Z3J5/giphy.gif)

## What is BurnBook?

**BurnBook** is a CLI tool that analyzes your codebase and delivers **brutal, hilarious, but educational** roast commentary about your code quality. Think of it as a linter, but with a personality disorder and a sick sense of humor.

### Why BurnBook?

- 😤 Most linters are boring and get ignored
- 😂 Comedy makes people actually read the output
- 🎯 Specific callouts help you learn what's wrong
- 🤖 AI-powered roasting (when available) for maximum devastation
- 📊 Beautiful HTML reports with charts

## Scoring System

| Score | Badge | Verdict |
|-------|-------|---------|
| 0-20 | 🔥 | **"This code is a war crime"** |
| 21-40 | 😬 | **"Did a ChatGPT free tier write this?"** |
| 41-60 | 😐 | **"Mid. Like gas station sushi."** |
| 61-80 | 👍 | **"Okay, not bad. Your mom would be proud."** |
| 81-100 | 🏆 | **"Chef's kiss. Ship it."** |

## Installation

```bash
# From PyPI (coming soon)
pip install burnbook

# From source
git clone https://github.com/burnbook/burnbook.git
cd burnbook
pip install -e .
```

## Quick Start

```bash
# Roast your current directory
burnbook roast .

# Roast a specific file
burnbook roast ./src/app.py

# Roast with nuclear severity
burnbook roast . --severity nuclear

# Generate an HTML report
burnbook report . --output report.html

# CI mode (fails if score < 60)
burnbook roast . --ci

# Offline mode (no AI roasting)
burnbook roast . --offline
```

## CLI Reference

### `burnbook roast`

```
Usage: burnbook roast [OPTIONS] TARGET

Arguments:
  TARGET  Path to file or directory to analyze (default: current directory)

Options:
  -l, --lang LANG         Language: python, javascript, typescript, go, rust, java, auto
  -s, --severity LEVEL    Roast severity: gentle, medium, brutal, nuclear  [default: brutal]
  -f, --format FORMAT     Output format: console, json, html  [default: console]
  --ci                    CI mode: exit non-zero if score < threshold
  --ci-threshold INTEGER  CI failure threshold  [default: 60]
  --offline               Offline mode: skip AI roasting
  --no-banner             Skip the ASCII banner
  --max-files INTEGER     Maximum files to analyze  [default: 500]
  --exclude PATTERN       Glob patterns to exclude (repeatable)
  -o, --output PATH       Output file path (for json/html)
  --version               Show version and exit
  --help                  Show this message and exit
```

### `burnbook report`

```
Usage: burnbook report [OPTIONS] TARGET

Generates a beautiful HTML report with charts and AI commentary.

Options:
  -o, --output PATH    Output HTML file path  [default: burnbook-report.html]
  -l, --lang LANG      Language to analyze
  --offline            Offline mode: skip AI roasting
  -s, --severity LEVEL Roast severity level  [default: brutal]
  --help               Show this message and exit
```

## Examples

### The Nuclear Option

```bash
$ burnbook roast . --severity nuclear

🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

Oh. My. God.

Your code has more red flags than a Soviet May Day parade.

I've seen better structure in a Jenga tower during an earthquake.

Your 'utils.py' is 847 lines long. That's not a utility module, that's a
lifestyle choice.

🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
```

### JSON Output for CI/CD

```bash
$ burnbook roast . --format json | jq '.score'
23

$ burnbook roast . --ci --ci-threshold 70
💥 CI FAILED: Score 23 < threshold 70
```

### HTML Report

```bash
$ burnbook report . --output roast.html
📊 HTML report saved to: roast.html

# Open in browser
open roast.html
```

The HTML report includes:
- 🎯 Score visualization with color-coded severity
- 📈 Radar chart showing category scores
- 🚨 Sortable issues table
- 🤖 AI roast commentary (if API key is set)
- 📊 Severity breakdown

## AI Roasting

BurnBook supports AI-powered roasting via OpenRouter or OpenAI.

### Setup

```bash
# Using OpenRouter (recommended - more models)
export OPENROUTER_API_KEY="your_key_here"

# Or using OpenAI directly
export OPENAI_API_KEY="your_key_here"
```

### Custom Model (optional)

```bash
export BURNBOOK_MODEL="openai/gpt-4o"  # OpenRouter format
# or
export BURNBOOK_MODEL="gpt-4o"          # OpenAI format
```

### Without AI

BurnBook works completely offline! It just won't have the AI commentary. Static roasts are still savage.

```bash
burnbook roast . --offline
```

## Pre-commit Hook

Automatically roast your code before every commit:

```bash
# Install the hook
burnbook install-hook

# Or manually add to .git/hooks/pre-commit:
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
echo "🔥 BurnBook is judging your code..."
burnbook roast . --ci --ci-threshold 50 --no-banner
EOF
chmod +x .git/hooks/pre-commit
```

## GitHub Actions Integration

```yaml
name: BurnBook

on: [push, pull_request]

jobs:
  roast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - run: pip install burnbook
      - run: burnbook roast . --ci --ci-threshold 60
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

## Supported Languages

| Language | Extensions | Status |
|----------|-----------|--------|
| Python | `.py` | ✅ Full |
| JavaScript | `.js`, `.jsx`, `.mjs`, `.cjs` | ✅ Full |
| TypeScript | `.ts`, `.tsx` | ✅ Full |
| Go | `.go` | ✅ Full |
| Rust | `.rs` | ✅ Full |
| Java | `.java` | ✅ Full |

## What BurnBook Checks

### Complexity
- Cyclomatic complexity
- Function length
- Nesting depth
- Callback hell (JS)

### Naming
- Single-letter names (beyond `i`, `j`, `k`)
- Visually ambiguous names (`l`, `O`, `I`)
- Cryptic abbreviations

### Security
- Hardcoded credentials
- SQL injection patterns
- `eval()` usage
- `unsafe` blocks (Rust)

### Style
- Long lines (>120 chars)
- Mixed indentation
- Inconsistent naming

### Documentation
- Missing docstrings
- TODO/FIXME comments
- Undocumented public APIs

### Dead Code
- Unused imports
- Empty exception handlers
- Debug print statements

### Testing
- Test coverage estimation
- Test file presence

## The Roast Levels

### Gentle 🌸
> "Consider adding docstrings to help future developers understand this code."

### Medium ⚡
> "This function has a complexity of 15. Maybe it could be split up?"

### Brutal 🔥 (default)
> "This function is more complex than my last relationship. And that ended in therapy."

### Nuclear 💀
> "SWEET MOTHER OF FUNCTIONS. This 847-line monstrosity has 47 if-statements and 12 nested loops. I've seen more readable obfuscated C. The Mars Climate Orbiter would have crashed just parsing this. Delete your editor and reevaluate your life choices."

## Project Structure

```
burnbook/
├── burnbook/
│   ├── __init__.py
│   ├── cli.py           # CLI entry point
│   ├── analyzer.py      # Core analysis engine
│   ├── roaster.py       # AI & static roasting
│   ├── formatters.py    # Console, JSON, HTML output
│   └── rules/
│       ├── __init__.py
│       ├── common_rules.py      # Universal rules
│       ├── python_rules.py      # Python-specific
│       ├── javascript_rules.py  # JS/TS-specific
│       ├── go_rules.py          # Go-specific
│       ├── rust_rules.py        # Rust-specific
│       └── java_rules.py        # Java-specific
├── tests/
│   ├── test_analyzer.py
│   ├── test_rules.py
│   ├── test_formatters.py
│   └── test_cli.py
├── docs/
├── pyproject.toml
├── setup.py
├── README.md
├── LICENSE
└── .gitignore
```

## Development

```bash
# Clone and setup
git clone https://github.com/burnbook/burnbook.git
cd burnbook
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=burnbook --cov-report=html

# Format code
black burnbook tests
ruff check burnbook tests --fix
```

## Contributing

We welcome contributions! Areas we need help with:

- Additional language support (C, C++, Ruby, PHP, Swift, etc.)
- More rules (check our issues for ideas)
- Better AI prompts
- Documentation
- Bug fixes

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Why "BurnBook"?

Named after the iconic burn book from *Mean Girls*, because every codebase has secrets, and we're here to expose them.

> "Four for you, Glen Coco! You go, Glen Coco!"
>
> — Damian

> "You can't sit with us."
>
> — BurnBook to your code

## License

MIT License — see [LICENSE](LICENSE)

## Acknowledgments

- Inspired by the pain of reviewing code at 3 AM
- Special thanks to every developer who ever wrote "TODO: fix this"
- The AI roast commentary is powered by [OpenRouter](https://openrouter.ai/)

---

<p align="center">
  <strong>🔥 BurnBook — Your code will never feel safe again. 🔥</strong>
</p>
