"""
Common rules that apply across all languages.
The universal code crimes.
"""

import re
from pathlib import Path
from typing import List

from burnbook.rules import BaseRule, Issue


class LongLineRule(BaseRule):
    """Lines that are too long to read without a neck brace."""
    rule_id = "CMN001"
    category = "style"
    severity = "low"
    max_length = 120

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            if len(line) > self.max_length:
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=self.max_length,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=f"Line is {len(line)} characters long. Horizontal scrolling is not a personality.",
                    snippet=line[:80] + "...",
                ))
        return issues


class TodoFixmeRule(BaseRule):
    """TODO/FIXME comments — the graveyard of good intentions."""
    rule_id = "CMN002"
    category = "dead_code"
    severity = "info"
    pattern = re.compile(r"\b(TODO|FIXME|HACK|XXX|TEMP|BUG|WTF)\b", re.IGNORECASE)

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            match = self.pattern.search(line)
            if match:
                tag = match.group(1).upper()
                messages = {
                    "TODO": "TODO comment — a promise you'll never keep.",
                    "FIXME": "FIXME — so you knew it was broken and shipped it anyway?",
                    "HACK": "HACK comment — at least you're honest about your crimes.",
                    "XXX": "XXX comment — even the code is embarrassed.",
                    "TEMP": "TEMP code — temporary, like your job security.",
                    "BUG": "BUG comment — you documented it but didn't fix it. Brave.",
                    "WTF": "WTF comment — we feel the same way about your code.",
                }
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=messages.get(tag, f"{tag} comment left unresolved."),
                    snippet=line.strip()[:100],
                ))
        return issues


class HardcodedCredentialRule(BaseRule):
    """Hardcoded secrets — leaving the front door unlocked and posting your address online."""
    rule_id = "CMN003"
    category = "security"
    severity = "critical"
    patterns = [
        re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']'),
        re.compile(r'(?i)(api_key|apikey|api-key)\s*=\s*["\'][^"\']{8,}["\']'),
        re.compile(r'(?i)(secret|token|auth)\s*=\s*["\'][^"\']{8,}["\']'),
        re.compile(r'(?i)(aws_access_key|aws_secret)\s*=\s*["\'][^"\']{8,}["\']'),
        re.compile(r'["\'](?:AKIA[0-9A-Z]{16})["\']'),  # AWS key pattern
        re.compile(r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]{20,}'),
        re.compile(r'(?i)private_key\s*=\s*["\']-----'),
    ]

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        # Skip test files and example files (check filename only, not full path)
        file_name = file_path.name.lower()
        if any(x in file_name for x in ["test", "spec", "example", "sample", ".env.example"]):
            return []

        for i, line in enumerate(lines, 1):
            for pattern in self.patterns:
                if pattern.search(line):
                    issues.append(Issue(
                        file=file_path,
                        line=i,
                        column=None,
                        category=self.category,
                        severity=self.severity,
                        rule_id=self.rule_id,
                        message="Hardcoded credential detected. Congratulations, you're one GitHub push away from a very bad day.",
                        snippet="[REDACTED for your protection]",
                    ))
                    break  # One issue per line
        return issues


class MagicNumberRule(BaseRule):
    """Magic numbers — mysterious digits that mean everything and explain nothing."""
    rule_id = "CMN004"
    category = "style"
    severity = "low"
    # Match numbers in code context (not in comments or strings)
    pattern = re.compile(r'(?<!["\'\w])(\b(?!0\b|1\b|2\b|100\b)\d{2,}\b)(?!["\'\w])')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            # Skip comments and pure assignments
            stripped = line.strip()
            if stripped.startswith(("#", "//", "/*", "*", "'")):
                continue
            if "=" in stripped and stripped.index("=") < 10:
                # It's likely a constant definition, let it slide
                continue
            matches = self.pattern.findall(line)
            if matches:
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=f"Magic number(s) {', '.join(matches[:3])} found. What does it mean? Nobody knows.",
                    snippet=line.strip()[:100],
                ))
        return issues


class EmptyExceptionHandlerRule(BaseRule):
    """Empty catch/except blocks — the ostrich approach to error handling."""
    rule_id = "CMN005"
    category = "style"
    severity = "high"
    patterns = [
        re.compile(r'except\s*(?:\w+)?\s*:\s*$'),  # Python: except:
        re.compile(r'catch\s*\(.*\)\s*\{\s*\}'),    # JS/Java: catch() {}
        re.compile(r'except\s+Exception\s*:\s*$'),   # Python broad except
    ]
    pass_pattern = re.compile(r'^\s*pass\s*$')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            for pattern in self.patterns:
                if pattern.search(line):
                    # Check if next line is just 'pass' or empty catch body
                    next_line = lines[i] if i < len(lines) else ""
                    if self.pass_pattern.match(next_line) or "pass" in next_line:
                        issues.append(Issue(
                            file=file_path,
                            line=i,
                            column=None,
                            category=self.category,
                            severity=self.severity,
                            rule_id=self.rule_id,
                            message="Empty exception handler. 'Catching errors and doing nothing' is not error handling, it's denial.",
                            snippet=line.strip()[:100],
                        ))
                    break
        return issues


class ConsolePrintDebugRule(BaseRule):
    """Debug print/console.log statements left in production code."""
    rule_id = "CMN006"
    category = "style"
    severity = "medium"
    patterns = [
        re.compile(r'\bconsole\.(log|debug|warn|error)\s*\('),
        re.compile(r'\bprint\s*\('),
        re.compile(r'\bputs\s+'),
        re.compile(r'\bSystem\.out\.print'),
        re.compile(r'\bfmt\.Print'),
        re.compile(r'\bdbg!\s*\('),
    ]
    # False positive guards
    exclude_patterns = [
        re.compile(r'#.*print'),   # Python comment
        re.compile(r'//.*console'),  # JS comment
        re.compile(r'log\.(Info|Debug|Error|Warn|Fatal)'),  # proper logging
    ]

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith(("#", "//", "/*", "*")):
                continue
            if any(ep.search(line) for ep in self.exclude_patterns):
                continue
            for pattern in self.patterns:
                if pattern.search(line):
                    issues.append(Issue(
                        file=file_path,
                        line=i,
                        column=None,
                        category=self.category,
                        severity=self.severity,
                        rule_id=self.rule_id,
                        message="Debug print/console statement found. Your production logs are about to become a personal diary.",
                        snippet=line.strip()[:100],
                    ))
                    break
        return issues


class LargeFileSizeRule(BaseRule):
    """Files that are too long — the monolith."""
    rule_id = "CMN007"
    category = "complexity"
    severity = "medium"
    warning_threshold = 300
    critical_threshold = 1000

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        line_count = len(lines)
        if line_count >= self.critical_threshold:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity="high",
                rule_id=self.rule_id,
                message=(
                    f"This file has {line_count} lines. "
                    "That's not a file, that's a novel. Split it up before it gains sentience."
                ),
                snippet=None,
            )]
        elif line_count >= self.warning_threshold:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity="medium",
                rule_id=self.rule_id,
                message=(
                    f"This file is {line_count} lines long. "
                    "Single Responsibility Principle is crying in the corner."
                ),
                snippet=None,
            )]
        return []


class MixedIndentationRule(BaseRule):
    """Mixed tabs and spaces — a war crime that spans generations."""
    rule_id = "CMN008"
    category = "style"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        has_tabs = any(line.startswith("\t") for line in lines)
        has_spaces = any(line.startswith("  ") for line in lines)

        if has_tabs and has_spaces:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    "Mixed tabs and spaces detected. "
                    "This is how wars start. Pick one and commit."
                ),
                snippet=None,
            )]
        return []


RULES: List[BaseRule] = [
    LongLineRule(),
    TodoFixmeRule(),
    HardcodedCredentialRule(),
    MagicNumberRule(),
    EmptyExceptionHandlerRule(),
    ConsolePrintDebugRule(),
    LargeFileSizeRule(),
    MixedIndentationRule(),
]
