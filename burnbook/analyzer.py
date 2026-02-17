"""
BurnBook Analyzer - The crime scene investigator.
Collects evidence of code atrocities.
"""

import os
import time
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any
import fnmatch

from burnbook.rules import get_rules_for_language, detect_language


# File extensions by language
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".mjs", ".cjs", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "go": [".go"],
    "rust": [".rs"],
    "java": [".java"],
}

ALL_SUPPORTED_EXTENSIONS = {
    ext: lang
    for lang, exts in LANGUAGE_EXTENSIONS.items()
    for ext in exts
}

# Directories to always ignore
DEFAULT_IGNORE_DIRS = {
    "__pycache__", ".git", ".hg", ".svn", "node_modules",
    ".venv", "venv", "env", ".env", "dist", "build",
    "target", ".idea", ".vscode", "coverage", ".nyc_output",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "vendor",
    "third_party", ".eggs", "*.egg-info",
}

DEFAULT_IGNORE_FILES = {
    "*.min.js", "*.min.css", "*.bundle.js", "*.map",
    "*.lock", "package-lock.json", "yarn.lock", "Pipfile.lock",
    "poetry.lock", "go.sum",
}


class Analyzer:
    """
    The main analyzer. Walks your codebase, judges every file,
    and compiles a dossier of your code crimes.
    """

    def __init__(
        self,
        target: Path,
        language: Optional[str] = None,
        max_files: int = 500,
        exclude_patterns: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None,
    ):
        self.target = target
        self.language = language
        self.max_files = max_files
        self.exclude_patterns = exclude_patterns or []
        self.progress_callback = progress_callback
        self._files_analyzed = 0

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results."""
        start_time = time.time()

        if self.target.is_file():
            files = [self.target]
            detected_lang = self.language or detect_language(self.target)
        else:
            files = self._collect_files()
            detected_lang = self.language or self._detect_dominant_language(files)

        results = {
            "target": str(self.target),
            "language": detected_lang,
            "files_analyzed": 0,
            "total_lines": 0,
            "issues": [],
            "metrics": {},
            "score": 100,
            "category_scores": {},
            "roast_lines": [],
            "ai_roast": None,
            "elapsed_seconds": 0,
        }

        if not files:
            results["roast_lines"] = ["📭 No supported files found. Either your project is empty or you deleted everything in shame."]
            return results

        # Filter to detected language if specified
        if detected_lang and detected_lang != "auto":
            valid_exts = LANGUAGE_EXTENSIONS.get(detected_lang, [])
            if valid_exts:
                files = [f for f in files if f.suffix.lower() in valid_exts]

        files = files[:self.max_files]
        rules = get_rules_for_language(detected_lang)

        all_issues = []
        total_lines = 0

        step_size = max(1, 100 // max(len(files), 1))

        for i, file_path in enumerate(files):
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                total_lines += len(lines)

                for rule in rules:
                    try:
                        issues = rule.check(file_path, content, lines)
                        all_issues.extend(issues)
                    except Exception:
                        pass  # Rule failed, not our problem

                self._files_analyzed += 1

                if self.progress_callback:
                    self.progress_callback(step_size)

            except (PermissionError, OSError):
                pass

        if self.progress_callback:
            # Ensure we hit 100%
            remaining = 100 - (step_size * len(files))
            if remaining > 0:
                self.progress_callback(remaining)

        # Compute scores
        category_scores = self._compute_category_scores(all_issues, self._files_analyzed, total_lines)
        overall_score = self._compute_overall_score(category_scores)

        results.update({
            "files_analyzed": self._files_analyzed,
            "total_lines": total_lines,
            "issues": [i.to_dict() for i in all_issues],
            "metrics": self._compute_metrics(all_issues, self._files_analyzed, total_lines),
            "score": overall_score,
            "category_scores": category_scores,
            "elapsed_seconds": round(time.time() - start_time, 2),
        })

        return results

    def _collect_files(self) -> List[Path]:
        """Walk directory and collect supported source files."""
        files = []
        ignore_dirs = DEFAULT_IGNORE_DIRS.copy()

        for root, dirs, filenames in os.walk(self.target):
            root_path = Path(root)

            # Filter ignored directories in-place
            dirs[:] = [
                d for d in dirs
                if d not in ignore_dirs
                and not any(fnmatch.fnmatch(d, pat) for pat in ignore_dirs)
                and not self._is_excluded(root_path / d)
            ]

            for filename in filenames:
                file_path = root_path / filename

                if self._is_excluded(file_path):
                    continue

                if any(fnmatch.fnmatch(filename, pat) for pat in DEFAULT_IGNORE_FILES):
                    continue

                if file_path.suffix.lower() in ALL_SUPPORTED_EXTENSIONS:
                    files.append(file_path)

                if len(files) >= self.max_files:
                    return files

        return files

    def _is_excluded(self, path: Path) -> bool:
        """Check if path matches any exclusion pattern."""
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if fnmatch.fnmatch(str(path), pattern):
                return True
        return False

    def _detect_dominant_language(self, files: List[Path]) -> str:
        """Detect the dominant language based on file count."""
        lang_counts: Dict[str, int] = {}
        for f in files:
            lang = ALL_SUPPORTED_EXTENSIONS.get(f.suffix.lower())
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

        if not lang_counts:
            return "unknown"

        return max(lang_counts, key=lang_counts.get)

    def _compute_category_scores(
        self, issues: list, files_analyzed: int, total_lines: int
    ) -> Dict[str, int]:
        """Compute per-category scores (higher = better)."""
        categories = {
            "complexity": [],
            "naming": [],
            "security": [],
            "duplication": [],
            "documentation": [],
            "dead_code": [],
            "style": [],
            "testing": [],
        }

        severity_penalty = {
            "critical": 15,
            "high": 8,
            "medium": 4,
            "low": 1,
            "info": 0,
        }

        for issue in issues:
            cat = issue.category if hasattr(issue, "category") else issue.get("category", "style")
            sev = issue.severity if hasattr(issue, "severity") else issue.get("severity", "low")
            if cat in categories:
                categories[cat].append(severity_penalty.get(sev, 1))

        scores = {}
        baseline = max(files_analyzed * 2, 10)  # adjust penalty baseline

        for cat, penalties in categories.items():
            total_penalty = sum(penalties)
            # Score from 0-100, penalized per issue
            raw = max(0, 100 - int((total_penalty / baseline) * 30))
            scores[cat] = min(100, raw)

        return scores

    def _compute_overall_score(self, category_scores: Dict[str, int]) -> int:
        """Weighted average of category scores."""
        weights = {
            "complexity": 0.20,
            "security": 0.20,
            "naming": 0.10,
            "duplication": 0.15,
            "documentation": 0.10,
            "dead_code": 0.10,
            "style": 0.05,
            "testing": 0.10,
        }

        total_weight = sum(weights.values())
        weighted_sum = sum(
            category_scores.get(cat, 100) * w
            for cat, w in weights.items()
        )

        return max(0, min(100, int(weighted_sum / total_weight)))

    def _compute_metrics(
        self, issues: list, files_analyzed: int, total_lines: int
    ) -> Dict[str, Any]:
        """Compute summary metrics."""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        category_counts: Dict[str, int] = {}

        for issue in issues:
            sev = issue.severity if hasattr(issue, "severity") else issue.get("severity", "low")
            cat = issue.category if hasattr(issue, "category") else issue.get("category", "style")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "files_analyzed": files_analyzed,
            "total_lines": total_lines,
            "total_issues": len(issues),
            "issues_per_file": round(len(issues) / max(files_analyzed, 1), 2),
            "severity_counts": severity_counts,
            "category_counts": category_counts,
        }
