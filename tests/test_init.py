import os
import tempfile

import rita
from rita import get_version, compile_string, compile


def test_get_version_without_patch():
    version = get_version()
    parts = version.split(".")
    assert len(parts) == 3
    # Each part should be numeric
    for p in parts:
        assert p.isdigit()


def test_get_version_with_patch(monkeypatch):
    monkeypatch.setattr(rita, "__version__", (0, 7, 4, "beta1"))
    version = get_version()
    assert version == "0.7.4-beta1"


def test_compile_string_standalone():
    result = compile_string('WORD("hello")->MARK("GREETING")', use_engine="standalone")
    # Should return a RuleExecutor
    results = list(result.execute("hello world"))
    assert len(results) == 1
    assert results[0]["label"] == "GREETING"


def test_compile_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".rita", delete=False) as f:
        f.write('WORD("test")->MARK("TEST_LABEL")')
        f.flush()
        try:
            result = compile(f.name, use_engine="standalone")
            results = list(result.execute("test"))
            assert len(results) == 1
            assert results[0]["label"] == "TEST_LABEL"
        finally:
            os.unlink(f.name)


def test_compile_string_with_kwargs():
    result = compile_string(
        '{IN_LIST(items)}->MARK("MATCH")',
        use_engine="standalone",
        items=["hello", "world"]
    )
    results = list(result.execute("hello there"))
    assert len(results) == 1
    assert results[0]["label"] == "MATCH"
