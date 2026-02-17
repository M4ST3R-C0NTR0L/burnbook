"""
Tests for the BurnBook CLI.
"""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from burnbook.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_py_file(tmp_path):
    code = '''import os
import sys

password = "hardcoded123"

def bad_function(x, y, z, a, b, c):
    if x:
        if y:
            if z:
                for i in range(a):
                    while b:
                        try:
                            pass
                        except:
                            pass
    return None

# TODO: fix this
print("debug")
'''
    f = tmp_path / "sample.py"
    f.write_text(code)
    return tmp_path


class TestRoastCommand:
    def test_roast_directory(self, runner, sample_py_file):
        result = runner.invoke(cli, ["roast", str(sample_py_file), "--offline", "--no-banner"])
        assert result.exit_code == 0

    def test_roast_single_file(self, runner, sample_py_file):
        py_file = sample_py_file / "sample.py"
        result = runner.invoke(cli, ["roast", str(py_file), "--offline", "--no-banner"])
        assert result.exit_code == 0

    def test_roast_json_format(self, runner, sample_py_file):
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--format", "json"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "score" in data
        assert "issues" in data

    def test_roast_with_lang(self, runner, sample_py_file):
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--lang", "python", "--no-banner"
        ])
        assert result.exit_code == 0

    def test_ci_mode_pass(self, runner, tmp_path):
        """CI mode should pass for clean code."""
        clean = tmp_path / "clean.py"
        clean.write_text("def add(a, b):\n    return a + b\n")
        result = runner.invoke(cli, [
            "roast", str(tmp_path),
            "--offline", "--ci", "--ci-threshold", "0", "--no-banner"
        ])
        assert result.exit_code == 0

    def test_ci_mode_fail(self, runner, sample_py_file):
        """CI mode should fail for terrible code with high threshold."""
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--ci", "--ci-threshold", "99", "--no-banner"
        ])
        assert result.exit_code == 1

    def test_roast_html_output(self, runner, sample_py_file, tmp_path):
        output_file = tmp_path / "report.html"
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--format", "html",
            "--output", str(output_file), "--no-banner"
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content

    def test_roast_severity_gentle(self, runner, sample_py_file):
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--severity", "gentle", "--no-banner"
        ])
        assert result.exit_code == 0

    def test_roast_severity_nuclear(self, runner, sample_py_file):
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--severity", "nuclear", "--no-banner"
        ])
        assert result.exit_code == 0

    def test_roast_json_to_file(self, runner, sample_py_file, tmp_path):
        output_file = tmp_path / "output.json"
        result = runner.invoke(cli, [
            "roast", str(sample_py_file),
            "--offline", "--format", "json",
            "--output", str(output_file)
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "score" in data

    def test_roast_empty_directory(self, runner, tmp_path):
        result = runner.invoke(cli, [
            "roast", str(tmp_path),
            "--offline", "--no-banner"
        ])
        assert result.exit_code == 0

    def test_roast_exclude_pattern(self, runner, tmp_path):
        (tmp_path / "include.py").write_text("x = 1\n")
        (tmp_path / "exclude.py").write_text("password = 'hack'\n")
        result = runner.invoke(cli, [
            "roast", str(tmp_path),
            "--offline", "--exclude", "exclude.py",
            "--format", "json"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["files_analyzed"] == 1

    def test_roast_max_files(self, runner, tmp_path):
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text(f"x = {i}\n")
        result = runner.invoke(cli, [
            "roast", str(tmp_path),
            "--offline", "--max-files", "3",
            "--format", "json"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["files_analyzed"] <= 3


class TestReportCommand:
    def test_report_generates_html(self, runner, sample_py_file, tmp_path):
        output = tmp_path / "report.html"
        result = runner.invoke(cli, [
            "report", str(sample_py_file),
            "--offline", "--output", str(output)
        ])
        assert result.exit_code == 0
        assert output.exists()

    def test_report_default_output(self, runner, sample_py_file):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                "report", str(sample_py_file),
                "--offline"
            ])
            assert result.exit_code == 0
            assert Path("burnbook-report.html").exists()


class TestVersionFlag:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestHelpOutput:
    def test_main_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "roast" in result.output

    def test_roast_help(self, runner):
        result = runner.invoke(cli, ["roast", "--help"])
        assert result.exit_code == 0
        assert "--severity" in result.output
        assert "--offline" in result.output
        assert "--ci" in result.output
