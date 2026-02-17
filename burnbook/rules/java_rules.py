"""
Java rules — judging your enterprise patterns and XML nightmares.
"""

import re
from pathlib import Path
from typing import List

from burnbook.rules import BaseRule, Issue


class JavaGodClassRule(BaseRule):
    """God classes — one class to rule them all (and in the darkness bind them)."""
    rule_id = "JV001"
    category = "complexity"
    severity = "high"
    method_threshold = 20

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        # Count method definitions
        method_pattern = re.compile(
            r'(?:public|private|protected|static)\s+(?:final\s+)?(?:\w+\s+)+\w+\s*\('
        )
        methods = method_pattern.findall(content)

        if len(methods) > self.method_threshold:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"This class has ~{len(methods)} methods. "
                    "That's not a class, that's a monolith with delusions of grandeur. "
                    "Single Responsibility Principle is a suggestion, apparently."
                ),
                snippet=None,
            )]
        return []


class JavaSystemOutRule(BaseRule):
    """System.out.println — Java's console.log, equally shameful."""
    rule_id = "JV002"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'System\.out\.(print|println|printf)\s*\(')

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
                        "System.out.println detected. "
                        "This is Java, not a shell script. Use a logging framework. "
                        "Log4j exists (just... patch it first)."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:10]


class JavaEmptyCatchRule(BaseRule):
    """Empty catch blocks — swallowing exceptions like they never happened."""
    rule_id = "JV003"
    category = "style"
    severity = "high"
    pattern = re.compile(r'catch\s*\([^)]+\)\s*\{\s*\}')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        matches = self.pattern.finditer(content)
        issues = []
        for match in matches:
            line_num = content[:match.start()].count("\n") + 1
            issues.append(Issue(
                file=file_path,
                line=line_num,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    "Empty catch block detected. "
                    "Exceptions exist for a reason. "
                    "Swallowing them silently is how you debug 3 AM production fires."
                ),
                snippet="catch(...) {}  # 🚩",
            ))
        return issues[:5]


class JavaStringConcatLoopRule(BaseRule):
    """String concatenation in loops — O(n²) performance, proudly."""
    rule_id = "JV004"
    category = "complexity"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        in_loop = False
        brace_depth = 0
        loop_start = 0
        issues = []

        loop_pattern = re.compile(r'\b(for|while)\s*\(')
        concat_pattern = re.compile(r'\bString\s+\w+\s*\+?=\s*|\w+\s*\+=\s*"')

        for i, line in enumerate(lines, 1):
            if loop_pattern.search(line):
                in_loop = True
                loop_start = i
                brace_depth = 0

            if in_loop:
                brace_depth += line.count("{") - line.count("}")
                if concat_pattern.search(line) and "StringBuilder" not in content:
                    issues.append(Issue(
                        file=file_path,
                        line=i,
                        column=None,
                        category=self.category,
                        severity=self.severity,
                        rule_id=self.rule_id,
                        message=(
                            "String concatenation inside a loop without StringBuilder. "
                            "Every iteration creates a new String object. "
                            "Your garbage collector is judging you."
                        ),
                        snippet=line.strip()[:100],
                    ))

                if brace_depth <= 0:
                    in_loop = False

        return issues[:3]


class JavaRawTypeRule(BaseRule):
    """Raw types — generics are optional, apparently."""
    rule_id = "JV005"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'\b(List|Map|Set|ArrayList|HashMap|HashSet)\s+\w+\s*=')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            if self.pattern.search(line) and "<" not in line:
                issues.append(Issue(
                    file=file_path,
                    line=i,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        "Raw type usage detected. "
                        "Generics were added in Java 5 (2004). "
                        "It's time to use them."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:5]


RULES: List[BaseRule] = [
    JavaGodClassRule(),
    JavaSystemOutRule(),
    JavaEmptyCatchRule(),
    JavaStringConcatLoopRule(),
    JavaRawTypeRule(),
]
