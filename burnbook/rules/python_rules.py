"""
Python-specific rules — judging your snake code.
"""

import ast
import re
from pathlib import Path
from typing import List, Optional

from burnbook.rules import BaseRule, Issue


class PythonComplexityRule(BaseRule):
    """Cyclomatic complexity — when your function needs a map to navigate."""
    rule_id = "PY001"
    category = "complexity"
    severity = "high"
    threshold = 10

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._compute_complexity(node)
                if complexity > self.threshold:
                    severity = "critical" if complexity > 20 else "high"
                    issues.append(Issue(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        category=self.category,
                        severity=severity,
                        rule_id=self.rule_id,
                        message=(
                            f"Function '{node.name}' has cyclomatic complexity of {complexity}. "
                            f"That's not a function, that's a Choose Your Own Adventure book."
                        ),
                        snippet=f"def {node.name}(...)  # complexity: {complexity}",
                    ))
        return issues

    def _compute_complexity(self, node: ast.AST) -> int:
        """Compute McCabe cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (
                ast.If, ast.While, ast.For, ast.ExceptHandler,
                ast.With, ast.Assert, ast.comprehension,
            )):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


class PythonLongFunctionRule(BaseRule):
    """Functions that go on forever — the academic paper of code."""
    rule_id = "PY002"
    category = "complexity"
    severity = "medium"
    threshold = 50

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno)
                length = end_line - node.lineno
                if length > self.threshold:
                    severity = "high" if length > 100 else "medium"
                    issues.append(Issue(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        category=self.category,
                        severity=severity,
                        rule_id=self.rule_id,
                        message=(
                            f"Function '{node.name}' is {length} lines long. "
                            "If it needs a table of contents, it's too long."
                        ),
                        snippet=f"def {node.name}(...)  # {length} lines",
                    ))
        return issues


class PythonBadNamingRule(BaseRule):
    """Single-letter and cryptic variable names — the DaVinci Code of identifiers."""
    rule_id = "PY003"
    category = "naming"
    severity = "low"
    bad_names = re.compile(r'\b(l|O|I)\s*=')  # Visually confusing names
    single_letter = re.compile(r'\b([a-zA-Z])\s*=\s*[^=]')
    allowed_singles = {"i", "j", "k", "n", "x", "y", "z", "e", "f", "_"}

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Check function/class names
                if len(node.name) == 1:
                    issues.append(Issue(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        category=self.category,
                        severity="medium",
                        rule_id=self.rule_id,
                        message=(
                            f"Single-letter {'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class'} "
                            f"name '{node.name}'. Your future self will not remember what this does."
                        ),
                        snippet=None,
                    ))
                # Check for confusing names l/O/I
                if node.name in ("l", "O", "I"):
                    issues.append(Issue(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        category=self.category,
                        severity="medium",
                        rule_id=self.rule_id,
                        message=(
                            f"Name '{node.name}' is visually ambiguous. "
                            "Are you trying to gaslight your coworkers?"
                        ),
                        snippet=None,
                    ))

            if isinstance(node, ast.Name) and node.id in ("l", "O", "I"):
                issues.append(Issue(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    category=self.category,
                    severity="low",
                    rule_id=self.rule_id,
                    message=f"Variable '{node.id}' is visually ambiguous (l/O/I). This is how bugs hide.",
                    snippet=None,
                ))

        return issues[:20]  # Cap at 20 to avoid spam


class PythonBareExceptRule(BaseRule):
    """Bare except clauses — catching everything, handling nothing."""
    rule_id = "PY004"
    category = "style"
    severity = "high"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(Issue(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        "Bare 'except:' clause caught. This catches SystemExit and KeyboardInterrupt too. "
                        "You're not handling errors, you're hiding them."
                    ),
                    snippet="except:  # 🚩",
                ))
        return issues


class PythonMutableDefaultArgRule(BaseRule):
    """Mutable default arguments — the silent killer."""
    rule_id = "PY005"
    category = "style"
    severity = "high"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default is None:
                        continue
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        type_name = {ast.List: "list", ast.Dict: "dict", ast.Set: "set"}[type(default)]
                        issues.append(Issue(
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            category=self.category,
                            severity=self.severity,
                            rule_id=self.rule_id,
                            message=(
                                f"Mutable default argument ({type_name}) in '{node.name}'. "
                                "Classic Python gotcha. This object is shared across ALL calls. "
                                "Use None and initialize inside the function."
                            ),
                            snippet=f"def {node.name}(..., arg={type_name}())",
                        ))
        return issues


class PythonNoDocstringRule(BaseRule):
    """Missing docstrings — your code is undocumented chaos."""
    rule_id = "PY006"
    category = "documentation"
    severity = "low"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        undocumented = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Skip private/dunder and short functions
                if node.name.startswith("_"):
                    continue
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end = getattr(node, "end_lineno", node.lineno)
                    if end - node.lineno < 5:
                        continue  # Short functions get a pass

                if not (node.body and isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                    undocumented += 1

        if undocumented > 3:
            issues.append(Issue(
                file=file_path,
                line=None,
                column=None,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"{undocumented} public functions/classes without docstrings. "
                    "How is anyone supposed to know what this does? "
                    "Comments aren't optional, they're love letters to your future self."
                ),
                snippet=None,
            ))
        return issues


class PythonImportStarRule(BaseRule):
    """Wildcard imports — polluting your namespace since the dawn of time."""
    rule_id = "PY007"
    category = "style"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        issues.append(Issue(
                            file=file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            category=self.category,
                            severity=self.severity,
                            rule_id=self.rule_id,
                            message=(
                                f"'from {node.module} import *' detected. "
                                "Congratulations, you've imported unknown things into your namespace. "
                                "This is how name collisions happen."
                            ),
                            snippet=f"from {node.module} import *  # 🚩",
                        ))
        return issues


class PythonUnusedImportRule(BaseRule):
    """Unused imports — digital hoarding."""
    rule_id = "PY008"
    category = "dead_code"
    severity = "low"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        imported_names = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imported_names[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        name = alias.asname or alias.name
                        imported_names[name] = node.lineno

        # Check which names are used in the code (outside import lines)
        for name, lineno in imported_names.items():
            # Count occurrences outside of import lines
            count = sum(
                1 for i, line in enumerate(lines, 1)
                if i != lineno and re.search(rf'\b{re.escape(name)}\b', line)
            )
            if count == 0:
                issues.append(Issue(
                    file=file_path,
                    line=lineno,
                    column=None,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        f"Unused import '{name}'. "
                        "Imports are not decorations. Delete what you don't use."
                    ),
                    snippet=None,
                ))

        return issues[:10]  # Cap to avoid spam


class PythonGlobalVariableRule(BaseRule):
    """Global variables — everyone's problem, no one's responsibility."""
    rule_id = "PY009"
    category = "style"
    severity = "medium"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                issues.append(Issue(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    category=self.category,
                    severity=self.severity,
                    rule_id=self.rule_id,
                    message=(
                        f"'global' statement found for {', '.join(node.names)}. "
                        "Global mutable state is how you make everyone's life worse. "
                        "Use function parameters like a civilized developer."
                    ),
                    snippet=f"global {', '.join(node.names)}  # 🚩",
                ))
        return issues


class PythonSyntaxErrorRule(BaseRule):
    """Syntax errors — the most primal of code crimes."""
    rule_id = "PY010"
    category = "style"
    severity = "critical"

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        try:
            ast.parse(content)
            return []
        except SyntaxError as e:
            return [Issue(
                file=file_path,
                line=e.lineno,
                column=e.offset,
                category=self.category,
                severity=self.severity,
                rule_id=self.rule_id,
                message=(
                    f"Syntax error: {e.msg}. "
                    "The interpreter can't even parse this. "
                    "We're roasting broken code. Respect."
                ),
                snippet=str(e.text).strip()[:100] if e.text else None,
            )]


RULES: List[BaseRule] = [
    PythonComplexityRule(),
    PythonLongFunctionRule(),
    PythonBadNamingRule(),
    PythonBareExceptRule(),
    PythonMutableDefaultArgRule(),
    PythonNoDocstringRule(),
    PythonImportStarRule(),
    PythonUnusedImportRule(),
    PythonGlobalVariableRule(),
    PythonSyntaxErrorRule(),
]
