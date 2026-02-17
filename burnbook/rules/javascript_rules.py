"""
JavaScript/TypeScript rules — judging your callback pyramids.
"""

import re
from pathlib import Path
from typing import List

from burnbook.rules import BaseRule, Issue


class JSCallbackHellRule(BaseRule):
    """Callback hell — the pyramid of doom."""
    rule_id = "JS001"
    category = "complexity"
    severity = "high"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        max_nesting = 0
        for i, line in enumerate(lines, 1):
            # Count leading spaces/tabs to measure nesting
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            # Check for callbacks
            if re.search(r'function\s*\(|=>\s*\{', line):
                nesting_level = indent // 2  # Assume 2-space indent
                if nesting_level > max_nesting:
                    max_nesting = nesting_level
                if nesting_level >= 4:
                    issues.append(Issue(
                        file=file_path,
                        line=i,
                        column=indent,
                        category=self.category,
                        severity=self.severity,
                        rule_id=self.rule_id,
                        message=(
                            f"Callback nesting level {nesting_level} detected. "
                            "You've achieved Pyramid of Doom status. "
                            "async/await exists for a reason."
                        ),
                        snippet=line.strip()[:100],
                    ))
        return issues[:5]  # Cap


class JSVarDeclarationRule(BaseRule):
    """Using var — a relic from the dark ages."""
    rule_id = "JS002"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'\bvar\s+\w+')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
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
                        "'var' declaration detected. It's {year}. "
                        "Use 'const' or 'let'. 'var' hoisting is not a feature, it's a trap."
                    ).format(year=2024),
                    snippet=line.strip()[:100],
                ))
        return issues[:10]


class JSConsoleLogRule(BaseRule):
    """console.log left in production — your secrets in plaintext."""
    rule_id = "JS003"
    category = "style"
    severity = "medium"
    pattern = re.compile(r'\bconsole\.(log|debug|trace)\s*\(')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
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
                        "console.log found. "
                        "This is your debugging diary exposed to all browser users. "
                        "Use a real logger."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:10]


class JSEqualityRule(BaseRule):
    """Using == instead of === — type coercion Russian roulette."""
    rule_id = "JS004"
    category = "style"
    severity = "medium"
    # Match == but not === or !== or >=, <=
    pattern = re.compile(r'(?<![=!<>])={2}(?!=)')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
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
                        "'==' used instead of '==='. "
                        "Did you know '' == 0 is true in JavaScript? "
                        "Type coercion is not your friend."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues[:10]


class JSAnyTypeRule(BaseRule):
    """TypeScript 'any' — defeating the purpose of TypeScript."""
    rule_id = "JS005"
    category = "style"
    severity = "medium"
    pattern = re.compile(r':\s*any\b')

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        # Only check TypeScript files
        if file_path.suffix not in (".ts", ".tsx"):
            return []

        issues = []
        any_count = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if self.pattern.search(line):
                any_count += 1

        if any_count > 0:
            issues.append(Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Found {any_count} 'any' type annotation(s). "
                    "You're using TypeScript but opted out of type safety. "
                    "At that point, just use JavaScript and own it."
                ),
                snippet=None,
            ))
        return issues


class JSEvalUsageRule(BaseRule):
    """eval() — giving the internet a keyboard to your computer."""
    rule_id = "JS006"
    category = "security"
    severity = "critical"
    pattern = re.compile(r'\beval\s*\(')

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
                        "eval() detected. "
                        "eval() is evil. It's in the name: eval. EVIL. "
                        "This is an XSS vulnerability waiting to happen."
                    ),
                    snippet=line.strip()[:100],
                ))
        return issues


class JSPromiseChainingRule(BaseRule):
    """Excessive .then() chaining — async before async/await existed."""
    rule_id = "JS007"
    category = "style"
    severity = "low"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        # Count .then( occurrences per function-ish block
        then_count = content.count(".then(")
        if then_count >= 5:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Found {then_count} .then() chains. "
                    "Promise chaining this deep is how you lose your sanity. "
                    "async/await is right there."
                ),
                snippet=None,
            )]
        return []


class JSNoSemicolonRule(BaseRule):
    """Missing semicolons — ASI playing god with your code."""
    rule_id = "JS008"
    category = "style"
    severity = "info"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        # Skip TypeScript (it's more lenient) and JSX
        if file_path.suffix in (".tsx", ".ts"):
            return []

        missing = 0
        for line in lines:
            stripped = line.rstrip()
            if not stripped:
                continue
            # Lines that should end with semicolons
            if (stripped and not stripped.endswith((";", "{", "}", "//", ",", "(", "[", "*/"))
                    and re.search(r'\b(const|let|var|return|throw|break|continue)\b', stripped)
                    and not stripped.strip().startswith(("//", "/*", "*"))):
                missing += 1

        if missing > 5:
            return [Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"~{missing} potential missing semicolons detected. "
                    "ASI (Automatic Semicolon Insertion) is not a substitute for discipline."
                ),
                snippet=None,
            )]
        return []


RULES: List[BaseRule] = [
    JSCallbackHellRule(),
    JSVarDeclarationRule(),
    JSConsoleLogRule(),
    JSEqualityRule(),
    JSAnyTypeRule(),
    JSEvalUsageRule(),
    JSPromiseChainingRule(),
    JSNoSemicolonRule(),
]
