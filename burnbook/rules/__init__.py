"""
BurnBook Rules Engine - The judges' panel.
Each rule is a specific code quality check.
"""

from pathlib import Path
from typing import List, Optional
import dataclasses


@dataclasses.dataclass
class Issue:
    """Represents a single code quality violation."""
    file: Optional[Path]
    line: Optional[int]
    column: Optional[int]
    category: str          # complexity, naming, security, duplication, etc.
    severity: str          # critical, high, medium, low, info
    rule_id: str           # e.g., "PY001"
    message: str           # human-readable
    snippet: Optional[str] = None  # code snippet

    def to_dict(self) -> dict:
        return {
            "file": str(self.file) if self.file else None,
            "line": self.line,
            "column": self.column,
            "category": self.category,
            "severity": self.severity,
            "rule_id": self.rule_id,
            "message": self.message,
            "snippet": self.snippet,
        }


class BaseRule:
    """Base class for all rules."""
    rule_id: str = "BASE000"
    category: str = "style"
    severity: str = "low"
    language: str = "all"
    description: str = ""

    def check(self, file_path: Path, content: str, lines: List[str]) -> List[Issue]:
        raise NotImplementedError


def get_rules_for_language(language: Optional[str]) -> List[BaseRule]:
    """Return the appropriate rule set for a language."""
    from burnbook.rules import common_rules

    rules: List[BaseRule] = list(common_rules.RULES)

    if language == "python":
        from burnbook.rules import python_rules
        rules.extend(python_rules.RULES)
    elif language in ("javascript", "typescript"):
        from burnbook.rules import javascript_rules
        rules.extend(javascript_rules.RULES)
    elif language == "go":
        from burnbook.rules import go_rules
        rules.extend(go_rules.RULES)
    elif language == "rust":
        from burnbook.rules import rust_rules
        rules.extend(rust_rules.RULES)
    elif language == "java":
        from burnbook.rules import java_rules
        rules.extend(java_rules.RULES)
    else:
        # Unknown language: try all language rules
        from burnbook.rules import python_rules, javascript_rules, go_rules, rust_rules, java_rules
        rules.extend(python_rules.RULES)
        rules.extend(javascript_rules.RULES)
        rules.extend(go_rules.RULES)
        rules.extend(rust_rules.RULES)
        rules.extend(java_rules.RULES)

    return rules


def detect_language(file_path: Path) -> str:
    """Detect language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
    }
    return ext_map.get(file_path.suffix.lower(), "unknown")
