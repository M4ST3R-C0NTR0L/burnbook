# Contributing to BurnBook

First off, thanks for wanting to contribute! BurnBook exists because developers need to hear the truth about their code, and we'd love your help making that truth even more devastating (and helpful).

## How to Contribute

### Reporting Bugs

If you found a bug:
1. Check if it's already reported in [Issues](https://github.com/burnbook/burnbook/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Sample code that triggers the issue
   - Your Python version and OS

### Suggesting Rules

Have an idea for a new rule? Great! Open an issue with:
- The rule name/description
- What it should detect
- Severity level (critical/high/medium/low/info)
- Sample code that should trigger it
- Why this matters

### Adding Language Support

Want to roast another language? Here's what you need:

1. Create `burnbook/rules/{language}_rules.py`
2. Implement rules extending `BaseRule`
3. Add to `get_rules_for_language()` in `rules/__init__.py`
4. Add tests in `tests/test_rules.py`
5. Update README.md supported languages table

### Code Style

We use:
- **Black** for formatting (line length: 100)
- **Ruff** for linting
- **Pytest** for testing

```bash
# Format
black burnbook tests

# Lint
ruff check burnbook tests --fix

# Test
pytest
```

### Pull Request Process

1. Fork the repo
2. Create a branch: `git checkout -b feature/amazing-rule`
3. Make your changes
4. Add tests
5. Ensure all tests pass
6. Update documentation
7. Submit PR

## Development Setup

```bash
# Clone
git clone https://github.com/burnbook/burnbook.git
cd burnbook

# Create venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Run against your own code
burnbook roast . --offline
```

## Rule Writing Guide

### Basic Rule Template

```python
from burnbook.rules import BaseRule, Issue

class MyNewRule(BaseRule):
    rule_id = "PY999"  # Use prefix: PY=Python, JS=JS/TS, GO=Go, RS=Rust, JV=Java, CMN=Common
    category = "security"  # complexity, naming, security, style, dead_code, documentation
    severity = "high"  # critical, high, medium, low, info
    description = "What this rule does"
    
    def check(self, file_path, content, lines):
        issues = []
        # Your analysis logic here
        if self._detected_something(content):
            issues.append(Issue(
                file=file_path,
                line=42,  # or None
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message="Your savage roast message here",
                snippet=lines[41][:100] if lines else None,
            ))
        return issues
```

### Roast Message Tips

- Be specific about the actual issue
- Make it funny, but educational
- Reference real consequences (security, performance, maintainability)
- Keep it punchy (2-3 sentences max)

### Good Roast Messages

✅ **Good:**
```python
message=(
    "Hardcoded credential detected. "
    "Congratulations, you're one GitHub push away from a very bad day."
)
```

❌ **Bad:**
```python
message="This is bad code."  # Not funny, not specific
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_rules.py

# Specific test
pytest tests/test_rules.py::TestPythonComplexityRule

# With coverage
pytest --cov=burnbook --cov-report=html
```

### Writing Tests

```python
class TestMyNewRule:
    rule = MyNewRule()

    def test_detects_bad_thing(self):
        code = "bad_code_here()\n"
        issues = self.rule.check(FAKE_PATH, code, code.splitlines())
        assert len(issues) >= 1
        assert issues[0].severity == "high"

    def test_good_code_ok(self):
        code = "good_code_here()\n"
        issues = self.rule.check(FAKE_PATH, code, code.splitlines())
        assert len(issues) == 0
```

## Code of Conduct

- Be respectful (even when roasting code)
- Constructive feedback only
- No personal attacks
- Helpful > Hurtful

## Questions?

- Open an issue
- Start a discussion
- Email: contributors@burnbook.dev

## Roast Level Guidelines

When adding severity-aware features, here's how we think about roast levels:

| Level | Tone | Example |
|-------|------|---------|
| Gentle | Helpful mentor | "Consider adding docstrings" |
| Medium | Direct friend | "This function is too long" |
| Brutal | Sarcastic comedian | "This is... a choice" |
| Nuclear | Gordon Ramsay | "WHAT ARE YOU? A GOVERNMENT AGENCY?" |

---

**🔥 Remember: The goal is to make people *want* to fix their code, not make them quit programming. 🔥**
