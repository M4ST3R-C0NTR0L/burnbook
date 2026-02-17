# Changelog

All notable changes to BurnBook will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-XX-XX

### Added
- Initial release of BurnBook
- Code analysis for Python, JavaScript, TypeScript, Go, Rust, Java
- AI-powered roast commentary via OpenRouter/OpenAI
- Static roast mode (offline)
- Console, JSON, and HTML output formats
- CI/CD integration with exit codes
- Pre-commit hook support
- Severity levels: gentle, medium, brutal, nuclear
- Category-based scoring (complexity, naming, security, etc.)
- 40+ rules across all supported languages

### Rules Added

**Common Rules:**
- Long line detection
- TODO/FIXME comment tracking
- Hardcoded credential detection
- Magic number detection
- Empty exception handlers
- Debug print/console statements
- Large file detection
- Mixed indentation detection

**Python Rules:**
- Cyclomatic complexity
- Function length
- Bad naming (single letters, ambiguous chars)
- Bare except clauses
- Mutable default arguments
- Missing docstrings
- Wildcard imports
- Unused imports
- Global variable usage
- Syntax error detection

**JavaScript/TypeScript Rules:**
- Callback hell detection
- var usage (instead of const/let)
- console.log in production
- == vs === (loose equality)
- any type in TypeScript
- eval() usage
- Promise chaining depth
- Missing semicolons

**Go Rules:**
- Ignored errors (using _)
- panic() usage outside main/init
- Global mutexes
- Unbounded goroutines
- Long functions

**Rust Rules:**
- Excessive .unwrap() chains
- unsafe block usage
- Excessive .clone() calls
- panic! macro usage

**Java Rules:**
- God classes (too many methods)
- System.out.println usage
- Empty catch blocks
- String concatenation in loops
- Raw type usage (missing generics)

[1.0.0]: https://github.com/burnbook/burnbook/releases/tag/v1.0.0
