"""
Tests for BurnBook formatters.
"""
import json
import pytest

from burnbook.formatters import (
    JSONFormatter,
    HTMLFormatter,
    get_score_badge,
    get_score_label,
    get_score_color,
    SCORE_BANDS,
)


SAMPLE_RESULTS = {
    "target": "/fake/project",
    "language": "python",
    "files_analyzed": 5,
    "total_lines": 500,
    "score": 42,
    "elapsed_seconds": 1.23,
    "issues": [
        {
            "file": "/fake/project/app.py",
            "line": 10,
            "column": None,
            "category": "security",
            "severity": "critical",
            "rule_id": "CMN003",
            "message": "Hardcoded password detected.",
            "snippet": None,
        },
        {
            "file": "/fake/project/utils.py",
            "line": 42,
            "column": None,
            "category": "style",
            "severity": "medium",
            "rule_id": "PY001",
            "message": "Function too complex.",
            "snippet": "def func(...)  # complexity: 15",
        },
    ],
    "metrics": {
        "files_analyzed": 5,
        "total_lines": 500,
        "total_issues": 2,
        "issues_per_file": 0.4,
        "severity_counts": {
            "critical": 1,
            "high": 0,
            "medium": 1,
            "low": 0,
            "info": 0,
        },
        "category_counts": {"security": 1, "style": 1},
    },
    "category_scores": {
        "complexity": 70,
        "naming": 85,
        "security": 20,
        "duplication": 90,
        "documentation": 50,
        "dead_code": 80,
        "style": 65,
        "testing": 40,
    },
    "ai_roast": None,
}


class TestScoreBands:
    def test_score_0_20(self):
        badge = get_score_badge(10)
        label = get_score_label(10)
        assert badge == "🔥"
        assert "war crime" in label.lower()

    def test_score_21_40(self):
        badge = get_score_badge(30)
        assert badge == "😬"

    def test_score_41_60(self):
        badge = get_score_badge(50)
        assert badge == "😐"

    def test_score_61_80(self):
        badge = get_score_badge(70)
        assert badge == "👍"

    def test_score_81_100(self):
        badge = get_score_badge(90)
        assert badge == "🏆"

    def test_score_100(self):
        badge = get_score_badge(100)
        label = get_score_label(100)
        assert badge == "🏆"
        assert "ship" in label.lower()

    def test_score_0(self):
        badge = get_score_badge(0)
        assert badge == "🔥"


class TestJSONFormatter:
    def setup_method(self):
        self.formatter = JSONFormatter()

    def test_returns_valid_json(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_contains_score(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert data["score"] == 42

    def test_contains_issues(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert len(data["issues"]) == 2

    def test_contains_verdict(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert "verdict" in data
        assert data["verdict"] == get_score_label(42)

    def test_contains_metadata(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert "burnbook_version" in data
        assert "generated_at" in data
        assert data["language"] == "python"

    def test_contains_category_scores(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        data = json.loads(output)
        assert "category_scores" in data
        assert "security" in data["category_scores"]

    def test_empty_results(self):
        empty = {
            "target": "/empty",
            "language": "python",
            "score": 100,
            "files_analyzed": 0,
            "elapsed_seconds": 0,
            "issues": [],
            "metrics": {},
            "category_scores": {},
            "ai_roast": None,
        }
        output = self.formatter.render(empty)
        data = json.loads(output)
        assert data["score"] == 100


class TestHTMLFormatter:
    def setup_method(self):
        self.formatter = HTMLFormatter()

    def test_returns_html_string(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        assert isinstance(output, str)
        assert output.strip().startswith("<!DOCTYPE html>")

    def test_contains_score(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        assert "42" in output

    def test_contains_issues(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        assert "Hardcoded password detected" in output

    def test_contains_chart_js(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        assert "Chart.js" in output or "chart.js" in output.lower()

    def test_contains_language(self):
        output = self.formatter.render(SAMPLE_RESULTS)
        assert "python" in output

    def test_with_ai_roast(self):
        results = dict(SAMPLE_RESULTS)
        results["ai_roast"] = {
            "overall": "This code is a dumpster fire.",
            "sections": [
                {
                    "category": "security",
                    "roast": "Your passwords are basically public announcements.",
                    "tip": "Use environment variables.",
                }
            ],
            "closing": "Please seek professional help.",
            "verdict": "Security nightmare.",
        }
        output = self.formatter.render(results)
        assert "dumpster fire" in output
        assert "AI Roast Master" in output

    def test_no_issues_message(self):
        results = dict(SAMPLE_RESULTS)
        results["issues"] = []
        output = self.formatter.render(results)
        assert "No issues found" in output

    def test_html_escaping(self):
        results = dict(SAMPLE_RESULTS)
        results["issues"] = [{
            "file": "/fake/app.py",
            "line": 1,
            "column": None,
            "category": "security",
            "severity": "critical",
            "rule_id": "CMN003",
            "message": "Issue with <script>alert('xss')</script>",
            "snippet": None,
        }]
        output = self.formatter.render(results)
        # The issue message should be escaped (not the Chart.js script tags)
        assert "<script>alert(" not in output
        assert "&lt;script&gt;alert(" in output
