"""
Rust rules — judging your unsafe blocks and unwrap chains.
"""

import re
from pathlib import Path
from typing import List

from burnbook.rules import BaseRule, Issue


class RustUnwrapChainRule(BaseRule):
    """.unwrap() everywhere — treating panics as a feature."""
    rule_id = "RS001"
    category = "style"
    severity = "high"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        unwrap_count = content.count(".unwrap()")
        expect_count = content.count(".expect(")

        issues = []
        if unwrap_count > 5:
            issues.append(Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Found {unwrap_count} .unwrap() calls. "
                    "The whole point of Result<T, E> is to handle errors. "
                    "You're using Rust but skipping its biggest selling point."
                ),
                snippet=None,
            ))
        return issues


class RustUnsafeBlockRule(BaseRule):
    """Unsafe blocks — Rust's safe-code ejector seat."""
    rule_id = "RS002"
    category = "security"
    severity = "high"
    pattern = re.compile(r'\bunsafe\s*\{')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            if self.pattern.search(line):
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        "unsafe block detected. "
                        "You've defeated Rust's entire memory safety guarantee. "
                        "You better have an extremely good reason."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues


class RustCloneRule(BaseRule):
    """Excessive .clone() — when you don't understand the borrow checker."""
    rule_id = "RS003"
    category = "style"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        clone_count = content.count(".clone()")
        if clone_count > 10:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Found {clone_count} .clone() calls. "
                    "Cloning your way out of borrow checker errors isn't a solution, "
                    "it's a performance disaster waiting to happen."
                ),
                snippet=None,
            )]
        return []


class RustPanicMacroRule(BaseRule):
    """panic! macro — the surrender flag of error handling."""
    rule_id = "RS004"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'\bpanic!\s*\(')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if self.pattern.search(line):
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        "panic!() macro used. "
                        "This will crash your thread. Return an Err() instead."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:5]


RULES: List[BaseRule] = [
    RustUnwrapChainRule(),
    RustUnsafeBlockRule(),
    RustCloneRule(),
    RustPanicMacroRule(),
]
