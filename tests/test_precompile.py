import pytest

from rita.precompile import precompile

from utils import raw_compare


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


def test_alias():
    rules = """
    numbers = {"one", "two", "three"}
    @alias IN_LIST IL
    @alias MARK M
    
    IL(numbers)->M("HELLO")
    """

    expected = """
    numbers = {"one", "two", "three"}    

    IN_LIST(numbers)->MARK("HELLO")
    """

    result = precompile(rules.strip())
    raw_compare(expected, result)

