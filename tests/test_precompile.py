import pytest

from rita.precompile import precompile


def test_rule_import():
    rules = """
    @import "examples/simple-match.rita"
    """

    result = precompile(rules.strip())
    with open("examples/simple-match.rita", "r") as f:
        assert result == f.read()


def test_cyclical_import():
    rules = """
    @import "examples/cyclical-import.rita"
    """

    with pytest.raises(RuntimeError):
        precompile(rules)
