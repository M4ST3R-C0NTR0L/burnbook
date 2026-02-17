"""
Tests for individual rules.
"""

import pytest
from pathlib import Path

from burnbook.rules.python_rules import (
    PythonComplexityRule,
    PythonBareExceptRule,
    PythonMutableDefaultArgRule,
    PythonImportStarRule,
    PythonUnusedImportRule,
    PythonSyntaxErrorRule,
    PythonNoDocstringRule,
)
from burnbook.rules.common_rules import (
    HardcodedCredentialRule,
    TodoFixmeRule,
    LongLineRule,
    ConsolePrintDebugRule,
    LargeFileSizeRule,
    MixedIndentationRule,
)
from burnbook.rules.javascript_rules import (
    JSVarDeclarationRule,
    JSEvalUsageRule,
    JSEqualityRule,
    JSAnyTypeRule,
)
from burnbook.rules.go_rules import GoErrorIgnoreRule, GoPanicUsageRule
from burnbook.rules.rust_rules import RustUnwrapChainRule, RustUnsafeBlockRule


FAKE_PATH = Path("/fake/file.py")
FAKE_JS_PATH = Path("/fake/file.js")
FAKE_TS_PATH = Path("/fake/file.ts")
FAKE_GO_PATH = Path("/fake/file.go")
FAKE_RS_PATH = Path("/fake/file.rs")


def make_lines(content: str):
    return content.splitlines()


# ── Python Rules ──────────────────────────────────────────────────────────────

class TestPythonComplexityRule:
    rule = PythonComplexityRule()

    def test_simple_function_no_issues(self):
        code = "def add(a, b):\n    return a + b\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_complex_function_flagged(self):
        code = """
def complex_func(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            for i in range(10):
                                while True:
                                    if a and b and c:
                                        pass
"""
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_syntax_error_returns_empty(self):
        code = "def broken(:\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert issues == []


class TestPythonBareExcept:
    rule = PythonBareExceptRule()

    def test_bare_except_flagged(self):
        code = "try:\n    pass\nexcept:\n    pass\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_specific_except_ok(self):
        code = "try:\n    pass\nexcept ValueError:\n    pass\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestPythonMutableDefault:
    rule = PythonMutableDefaultArgRule()

    def test_list_default_flagged(self):
        code = "def func(items=[]):\n    return items\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_dict_default_flagged(self):
        code = "def func(cfg={}):\n    return cfg\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_none_default_ok(self):
        code = "def func(items=None):\n    if items is None:\n        items = []\n    return items\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_string_default_ok(self):
        code = "def func(name='world'):\n    return name\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestPythonImportStar:
    rule = PythonImportStarRule()

    def test_wildcard_import_flagged(self):
        code = "from os.path import *\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_normal_import_ok(self):
        code = "from os.path import join, exists\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestPythonSyntaxError:
    rule = PythonSyntaxErrorRule()

    def test_valid_code_ok(self):
        code = "x = 1 + 2\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_syntax_error_flagged(self):
        code = "def broken(:\n    pass\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1
        assert issues[0].severity == "critical"


# ── Common Rules ──────────────────────────────────────────────────────────────

class TestHardcodedCredentials:
    rule = HardcodedCredentialRule()

    def test_hardcoded_password_flagged(self):
        code = 'password = "supersecret123"\n'
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1
        assert issues[0].severity == "critical"

    def test_hardcoded_api_key_flagged(self):
        code = 'api_key = "sk-abc123def456ghi789jkl"\n'
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_env_var_ok(self):
        code = 'password = os.environ.get("PASSWORD")\n'
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_test_file_skipped(self):
        test_path = Path("/fake/test_file.py")
        code = 'password = "testpassword123"\n'
        issues = self.rule.check(test_path, code, make_lines(code))
        assert len(issues) == 0


class TestTodoFixme:
    rule = TodoFixmeRule()

    def test_todo_flagged(self):
        code = "# TODO: fix this later\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_fixme_flagged(self):
        code = "# FIXME: broken on edge case\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_clean_comment_ok(self):
        code = "# This is a normal comment\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestLongLine:
    rule = LongLineRule()

    def test_long_line_flagged(self):
        code = "x = " + "a" * 130 + "\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_normal_line_ok(self):
        code = "x = 1 + 2\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestLargeFile:
    rule = LargeFileSizeRule()

    def test_small_file_ok(self):
        code = "\n".join([f"x = {i}" for i in range(10)])
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_large_file_flagged(self):
        code = "\n".join([f"x = {i}" for i in range(1100)])
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1


class TestMixedIndentation:
    rule = MixedIndentationRule()

    def test_mixed_indentation_flagged(self):
        code = "def f():\n    x = 1\n\tif True:\n\t\tpass\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_consistent_spaces_ok(self):
        code = "def f():\n    x = 1\n    if True:\n        pass\n"
        issues = self.rule.check(FAKE_PATH, code, make_lines(code))
        assert len(issues) == 0


# ── JavaScript Rules ──────────────────────────────────────────────────────────

class TestJSVarDeclaration:
    rule = JSVarDeclarationRule()

    def test_var_flagged(self):
        code = "var x = 1;\n"
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_const_ok(self):
        code = "const x = 1;\n"
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) == 0

    def test_let_ok(self):
        code = "let x = 1;\n"
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestJSEval:
    rule = JSEvalUsageRule()

    def test_eval_flagged(self):
        code = 'eval("malicious code");\n'
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) >= 1
        assert issues[0].severity == "critical"

    def test_no_eval_ok(self):
        code = "const x = JSON.parse(data);\n"
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestJSEquality:
    rule = JSEqualityRule()

    def test_loose_equality_flagged(self):
        code = 'if (x == "hello") {}\n'
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_strict_equality_ok(self):
        code = 'if (x === "hello") {}\n'
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestJSAnyType:
    rule = JSAnyTypeRule()

    def test_any_in_typescript_flagged(self):
        code = "function fn(x: any): any { return x; }\n"
        issues = self.rule.check(FAKE_TS_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_any_in_js_ignored(self):
        code = "function fn(x: any): any { return x; }\n"
        issues = self.rule.check(FAKE_JS_PATH, code, make_lines(code))
        assert len(issues) == 0  # Not a .ts file


# ── Go Rules ──────────────────────────────────────────────────────────────────

class TestGoErrorIgnore:
    rule = GoErrorIgnoreRule()

    def test_ignored_error_flagged(self):
        code = "result, _ := doSomething()\n"
        issues = self.rule.check(FAKE_GO_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_handled_error_ok(self):
        code = "result, err := doSomething()\nif err != nil { return err }\n"
        issues = self.rule.check(FAKE_GO_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestGoPanic:
    rule = GoPanicUsageRule()

    def test_panic_flagged(self):
        code = 'panic("something went wrong")\n'
        issues = self.rule.check(FAKE_GO_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_no_panic_ok(self):
        code = 'return fmt.Errorf("something went wrong")\n'
        issues = self.rule.check(FAKE_GO_PATH, code, make_lines(code))
        assert len(issues) == 0


# ── Rust Rules ────────────────────────────────────────────────────────────────

class TestRustUnwrap:
    rule = RustUnwrapChainRule()

    def test_many_unwraps_flagged(self):
        lines = [f"let x{i} = result_{i}.unwrap();" for i in range(10)]
        code = "\n".join(lines)
        issues = self.rule.check(FAKE_RS_PATH, code, make_lines(code))
        assert len(issues) >= 1

    def test_few_unwraps_ok(self):
        code = "let x = result.unwrap();\nlet y = other.unwrap();\n"
        issues = self.rule.check(FAKE_RS_PATH, code, make_lines(code))
        assert len(issues) == 0


class TestRustUnsafe:
    rule = RustUnsafeBlockRule()

    def test_unsafe_block_flagged(self):
        code = "unsafe {\n    let ptr = std::ptr::null();\n}\n"
        issues = self.rule.check(FAKE_RS_PATH, code, make_lines(code))
        assert len(issues) >= 1
        assert issues[0].severity == "high"

    def test_no_unsafe_ok(self):
        code = "let x = vec![1, 2, 3];\n"
        issues = self.rule.check(FAKE_RS_PATH, code, make_lines(code))
        assert len(issues) == 0


# ── Scorer Tests ──────────────────────────────────────────────────────────────

class TestScoring:
    def test_score_within_range(self):
        from burnbook.analyzer import Analyzer
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            code = "x = 1\n"
            (Path(tmpdir) / "test.py").write_text(code)
            analyzer = Analyzer(target=Path(tmpdir), language="python")
            results = analyzer.analyze()
            assert 0 <= results["score"] <= 100

    def test_score_decreases_with_issues(self):
        from burnbook.analyzer import Analyzer
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            clean = Path(tmpdir) / "clean.py"
            clean.write_text("def add(a: int, b: int) -> int:\n    \"\"\"Add.\"\"\"\n    return a + b\n")
            analyzer_clean = Analyzer(target=clean, language="python")
            clean_results = analyzer_clean.analyze()

        with tempfile.TemporaryDirectory() as tmpdir:
            dirty = Path(tmpdir) / "dirty.py"
            dirty.write_text(
                'password = "secret"\n' * 5 +
                'from os import *\n' +
                'import sys\n' +  # unused
                'def x():\n    pass\n'
            )
            analyzer_dirty = Analyzer(target=dirty, language="python")
            dirty_results = analyzer_dirty.analyze()

        assert dirty_results["score"] <= clean_results["score"]
