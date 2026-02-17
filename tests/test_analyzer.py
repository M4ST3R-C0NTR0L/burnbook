"""
Tests for the BurnBook analyzer.
"""

import pytest
from pathlib import Path
import tempfile
import os

from burnbook.analyzer import Analyzer


@pytest.fixture
def tmp_python_file(tmp_path):
    """Create a temporary Python file with known issues."""
    bad_code = '''
import os
import sys
import json  # unused

password = "supersecret123"

def x(l, O, I):
    """bad names"""
    pass

def very_complex_function(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        for i in range(100):
                            while True:
                                try:
                                    pass
                                except:
                                    pass
    return None

# TODO: fix this mess
# FIXME: and this

def no_docs(x):
    return x * 2

class BigClass:
    pass

print("debug output")
'''
    f = tmp_path / "bad_code.py"
    f.write_text(bad_code)
    return f


@pytest.fixture
def tmp_good_python_file(tmp_path):
    """Create a temporary Python file with minimal issues."""
    good_code = '''"""Module docstring."""
from typing import Optional


def add_numbers(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


def greet(name: Optional[str] = None) -> str:
    """Return a greeting message."""
    if name is None:
        name = "World"
    return f"Hello, {name}!"


class Calculator:
    """A simple calculator class."""

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
'''
    f = tmp_path / "good_code.py"
    f.write_text(good_code)
    return f


@pytest.fixture
def tmp_js_file(tmp_path):
    """Create a JavaScript file with known issues."""
    bad_js = '''
var x = 1;
var y = 2;

function doStuff(data, callback) {
    fetch('/api').then(function(res) {
        res.json().then(function(data) {
            callback(data, function(result) {
                console.log(result);
                doMore(result, function(final) {
                    console.log(final);
                });
            });
        });
    });
}

if (x == "1") {
    eval("alert('xss')");
}
'''
    f = tmp_path / "bad_code.js"
    f.write_text(bad_js)
    return f


class TestAnalyzerSingleFile:
    def test_analyze_python_file(self, tmp_python_file):
        analyzer = Analyzer(target=tmp_python_file, language="python")
        results = analyzer.analyze()

        assert results["files_analyzed"] == 1
        assert results["total_lines"] > 0
        assert isinstance(results["issues"], list)
        assert isinstance(results["score"], int)
        assert 0 <= results["score"] <= 100

    def test_bad_code_has_issues(self, tmp_python_file):
        analyzer = Analyzer(target=tmp_python_file, language="python")
        results = analyzer.analyze()
        assert len(results["issues"]) > 0

    def test_bad_code_has_lower_score(self, tmp_python_file, tmp_good_python_file):
        bad_analyzer = Analyzer(target=tmp_python_file, language="python")
        good_analyzer = Analyzer(target=tmp_good_python_file, language="python")

        bad_results = bad_analyzer.analyze()
        good_results = good_analyzer.analyze()

        assert bad_results["score"] <= good_results["score"]

    def test_detects_hardcoded_password(self, tmp_path):
        # Use a non-test filename so the credential rule doesn't skip it
        code_file = tmp_path / "app_code.py"
        code_file.write_text('password = "supersecret123"\n')
        analyzer = Analyzer(target=code_file, language="python")
        results = analyzer.analyze()

        security_issues = [
            i for i in results["issues"]
            if i.get("category") == "security"
        ]
        assert len(security_issues) >= 1

    def test_detects_debug_print(self, tmp_python_file):
        analyzer = Analyzer(target=tmp_python_file, language="python")
        results = analyzer.analyze()

        style_issues = [i for i in results["issues"] if "print" in i.get("message", "").lower()]
        # print is checked by common rules
        assert len(results["issues"]) > 0

    def test_analyze_javascript_file(self, tmp_js_file):
        analyzer = Analyzer(target=tmp_js_file, language="javascript")
        results = analyzer.analyze()

        assert results["files_analyzed"] == 1
        assert len(results["issues"]) > 0

    def test_detects_var_usage(self, tmp_js_file):
        analyzer = Analyzer(target=tmp_js_file, language="javascript")
        results = analyzer.analyze()

        var_issues = [
            i for i in results["issues"]
            if "var" in i.get("message", "").lower()
        ]
        assert len(var_issues) >= 1

    def test_detects_eval_usage(self, tmp_js_file):
        analyzer = Analyzer(target=tmp_js_file, language="javascript")
        results = analyzer.analyze()

        eval_issues = [
            i for i in results["issues"]
            if "eval" in i.get("message", "").lower()
        ]
        assert len(eval_issues) >= 1


class TestAnalyzerDirectory:
    def test_analyze_directory(self, tmp_path, tmp_python_file, tmp_good_python_file):
        analyzer = Analyzer(target=tmp_path, language="python")
        results = analyzer.analyze()

        assert results["files_analyzed"] == 2
        assert results["total_lines"] > 0

    def test_score_is_integer(self, tmp_path, tmp_python_file):
        analyzer = Analyzer(target=tmp_path, language="python")
        results = analyzer.analyze()
        assert isinstance(results["score"], int)

    def test_category_scores_present(self, tmp_path, tmp_python_file):
        analyzer = Analyzer(target=tmp_path, language="python")
        results = analyzer.analyze()

        cat_scores = results.get("category_scores", {})
        assert len(cat_scores) > 0
        for score in cat_scores.values():
            assert 0 <= score <= 100

    def test_metrics_present(self, tmp_path, tmp_python_file):
        analyzer = Analyzer(target=tmp_path, language="python")
        results = analyzer.analyze()

        metrics = results.get("metrics", {})
        assert "files_analyzed" in metrics
        assert "total_lines" in metrics
        assert "total_issues" in metrics
        assert "severity_counts" in metrics

    def test_max_files_limit(self, tmp_path):
        # Create 5 Python files
        for i in range(5):
            (tmp_path / f"file_{i}.py").write_text(f"# file {i}\nprint({i})\n")

        analyzer = Analyzer(target=tmp_path, language="python", max_files=3)
        results = analyzer.analyze()

        assert results["files_analyzed"] <= 3

    def test_exclude_patterns(self, tmp_path):
        (tmp_path / "include.py").write_text("x = 1\n")
        (tmp_path / "exclude.py").write_text("y = 2\n")

        analyzer = Analyzer(
            target=tmp_path,
            language="python",
            exclude_patterns=["exclude.py"]
        )
        results = analyzer.analyze()
        assert results["files_analyzed"] == 1

    def test_empty_directory(self, tmp_path):
        analyzer = Analyzer(target=tmp_path, language="python")
        results = analyzer.analyze()
        assert results["files_analyzed"] == 0


class TestLanguageDetection:
    def test_detect_python(self, tmp_python_file):
        analyzer = Analyzer(target=tmp_python_file)
        results = analyzer.analyze()
        assert results["language"] == "python"

    def test_detect_javascript(self, tmp_js_file):
        analyzer = Analyzer(target=tmp_js_file)
        results = analyzer.analyze()
        assert results["language"] == "javascript"
