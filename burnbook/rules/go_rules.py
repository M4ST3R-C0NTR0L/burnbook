"""
Go rules — judging your gophers.
"""

import re
from pathlib import Path
from typing import List

from burnbook.rules import BaseRule, Issue


class GoErrorIgnoreRule(BaseRule):
    """Ignoring errors — the '_' of shame."""
    rule_id = "GO001"
    category = "style"
    severity = "high"
    pattern = re.compile(r',\s*_\s*:?=|_\s*=\s*\w+\(')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if self.pattern.search(line):
                # Specifically look for error ignored
                if re.search(r',\s*_\s*(?::?=)', line):
                    issues.append(Issue(
                        file=file_path,
                        line=i,
                        column=None,
                        category=self.category,
                        severity=self.severity,
                        rule_id=self.rule_id,
                        message=(
                            "Error return value ignored with '_'. "
                            "In Go, ignoring errors is ignoring reality. "
                            "This will bite you in production."
                        ),
                        snippet=line.strip()[:100],
                    ))
        return issues[:10]


class GoPanicUsageRule(BaseRule):
    """panic() in non-main/init code — the nuclear option."""
    rule_id = "GO002"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'\bpanic\s*\(')

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
                        "panic() found. Unless this is in main() or init(), "
                        "you're about to crash your entire service for a recoverable error. "
                        "Return errors like a Gopher."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:5]


class GoGlobalMutexRule(BaseRule):
    """Global mutexes — shared mutable state with extra steps."""
    rule_id = "GO003"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'^var\s+\w+\s+sync\.(Mutex|RWMutex)')

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
                        "Global mutex detected. "
                        "Global state protected by a mutex is still global state. "
                        "Encapsulate this in a struct."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues


class GoUnboundedGoroutineRule(BaseRule):
    """Goroutines without WaitGroups or context — fire and forget disasters."""
    rule_id = "GO004"
    category = "complexity"
    severity = "medium"
    go_pattern = re.compile(r'\bgo\s+\w+\s*\(')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        go_count = sum(1 for line in lines if self.go_pattern.search(line))
        has_waitgroup = "WaitGroup" in content or "sync.WaitGroup" in content
        has_context = "context." in content

        if go_count > 3 and not has_waitgroup and not has_context:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Found {go_count} goroutine launches without apparent WaitGroup or context. "
                    "Fire-and-forget goroutines are how you get memory leaks and unexplained crashes."
                ),
                snippet=None,
            )]
        return []


class GoLongFunctionRule(BaseRule):
    """Long functions in Go — your handler shouldn't be a saga."""
    rule_id = "GO005"
    category = "complexity"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        func_start = None
        func_name = ""
        brace_depth = 0
        func_pattern = re.compile(r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(')

        for i, line in enumerate(lines, 1):
            match = func_pattern.match(line)
            if match and brace_depth == 0:
                func_start = i
                func_name = match.group(1)

            brace_depth += line.count("{") - line.count("}")

            if func_start and brace_depth == 0 and i > func_start:
                func_length = i - func_start
                if func_length > 60:
                    issues.append(Issue(
                        file=file_path,
                        line=func_start,
                        column=None,
                        category=self.category,
                        severity="high" if func_length > 100 else "medium",
                        rule_id=self.rule_id,
                        message=(
                            f"Function '{func_name}' is {func_length} lines long. "
                            "Even Ken Thompson would be disappointed."
                        ),
                        snippet=f"func {func_name}(...)  # {func_length} lines",
                    ))
                func_start = None

        return issues[:5]


RULES: List[BaseRule] = [
    GoErrorIgnoreRule(),
    GoPanicUsageRule(),
    GoGlobalMutexRule(),
    GoUnboundedGoroutineRule(),
    GoLongFunctionRule(),
]
