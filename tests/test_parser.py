import logging
import pytest

from rita.parser import RitaParser
from rita.config import SessionConfig


@pytest.fixture
def config():
    return SessionConfig()


def test_parser_empty_rules(config):
    p = RitaParser(config)
    p.build()
    results = p.parse("")
    assert len(results) == 0


def test_parser_any_macro_wo_args_w_type(config):
    p = RitaParser(config)
    p.build()

    results = p.parse('ANY -> MARK("PlaceHolder")')
    assert len(results) == 1


def test_parser_any_macro_w_args_w_type(config):
    p = RitaParser(config)
    p.build()

    results = p.parse('{WORD("arg1")} -> MARK("PlaceHolder")')
    assert len(results) == 1


def test_parser_nested_macro(config):
    p = RitaParser(config)
    p.build()

    results = p.parse('{ANY, WORD("test")} -> MARK("Test")')
    assert len(results) == 1
    for result in results:
        print(result())


def test_parser_assign_literal_and_ignore_it(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        my_variable = "Test"

        {WORD("something")} -> MARK("TEST")
        """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "something", None)]} == rules


def test_parser_assign_literal_and_use_it(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        my_variable = "Test"

        {WORD(my_variable)} -> MARK("TEST")
        """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "Test", None)]} == rules


def test_parser_just_assign_macro(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        x = WORD("Test")
        """
    )
    assert len(results) == 1


def test_parser_assign_two_variables(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        a = "A"
        b = "B"
        """
    )
    assert len(results) == 2


def test_parser_assign_macro_and_use_it(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        my_variable = WORD("Test")

        {my_variable} -> MARK("TEST")
        """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "Test", None)]} == rules


def test_parser_import_module(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        IMPORT("rita.modules.fuzzy") -> EXEC

        FUZZY("test") -> MARK("FUZZY_MATCH")
        """
    )

    assert len(results) == 2


def test_parser_import_module_shortcut(config, caplog):
    caplog.set_level(logging.INFO)
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        !IMPORT("rita.modules.fuzzy")

        FUZZY("test") -> MARK("FUZZY_MATCH")
        """
    )

    assert len(results) == 2


def test_parser_config(config):
    p = RitaParser(config)
    p.build(debug=True)

    p.parse(
        """
        !CONFIG("foo", "bar")
        !CONFIG("testing", "1")
        """
    )

    assert config.foo == "bar"
    assert config.testing


def test_parser_list_w_one_item(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        members = { "one" }

        IN_LIST(members) -> MARK("MEMBER")
        """
    )

    assert len(results) == 2


def test_parser_list_w_two_items(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        """
        members = {"one", "two"}

        IN_LIST(members) -> MARK("MEMBER")
        """
    )

    assert len(results) == 2


def test_parser_literal_w_escape(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        r'WORD("Hello \"WORLD\"") -> MARK("TEST")'
    )

    assert len(results) == 1


def test_parser_pattern_in_variable(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        '''
        Complex_Number = { NUM+, WORD("/")?, NUM? }
        {PATTERN(Complex_Number), WORD("inch")}->MARK("WIDTH")
        '''
    )

    print(results)
    assert len(results) == 2


def test_pattern_with_escaped_characters(config):
    p = RitaParser(config)
    p.build(debug=True)

    results = p.parse(
        '''
        special = { '"', "*", "-" }
        IN_LIST(special)->MARK("TEST")
        '''
    )

    assert len(results) > 0

    rules = results[1]()

    assert {"label": "TEST", "data": [("any_of", ["\"", "*", "-"], None)]} == rules
