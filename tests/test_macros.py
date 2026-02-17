import types

import pytest

from rita.config import SessionConfig
from rita.utils import ExtendedOp
from rita.macros import (
    resolve_value, ANY, PUNCT, MARK, ASSIGN, IN_LIST,
    PATTERN, NESTED, WORD, NUM, POS, LEMMA, ENTITY,
    PREFIX, IMPORT, CONFIG, EXEC,
)


@pytest.fixture
def cfg():
    return SessionConfig()


class TestResolveValue:
    def test_string(self, cfg):
        assert resolve_value("hello", cfg) == "hello"

    def test_tuple(self, cfg):
        t = ("value", "test", ExtendedOp(None))
        assert resolve_value(t, cfg) is t

    def test_list(self, cfg):
        lst = ["a", "b"]
        assert resolve_value(lst, cfg) is lst

    def test_generator(self, cfg):
        def gen():
            yield "a"
            yield "b"
        result = resolve_value(gen(), cfg)
        assert result[0] == "either"
        assert result[1] == ["a", "b"]
        assert isinstance(result[2], ExtendedOp)

    def test_callable(self, cfg):
        called = {}

        def fn(config):
            called["config"] = config
            return "result"

        result = resolve_value(fn, cfg)
        assert result == "result"
        assert called["config"] is cfg


class TestAny:
    def test_basic(self, cfg):
        result = ANY(config=cfg)
        assert result == ("any", None, ExtendedOp(None))

    def test_with_op(self, cfg):
        result = ANY(config=cfg, op="+")
        assert result[0] == "any"
        assert result[2].value == "+"


class TestPunct:
    def test_basic(self, cfg):
        result = PUNCT(config=cfg)
        assert result == ("punct", None, ExtendedOp(None))


class TestMark:
    def test_basic(self, cfg):
        result = MARK("LABEL", ("value", "test", ExtendedOp(None)), config=cfg)
        assert result["label"] == "LABEL"
        assert result["data"] == ("value", "test", ExtendedOp(None))


class TestWord:
    def test_with_arg(self, cfg):
        result = WORD("test", config=cfg)
        assert result[0] == "value"
        assert result[1] == "test"
        assert isinstance(result[2], ExtendedOp)

    def test_without_arg(self, cfg):
        result = WORD(config=cfg)
        assert result[0] == "regex"
        assert r"(\w|['_-])" in result[1]

    def test_with_op(self, cfg):
        result = WORD("test", config=cfg, op="+")
        assert result[2].value == "+"


class TestNum:
    def test_with_arg(self, cfg):
        result = NUM("42", config=cfg)
        assert result[0] == "value"
        assert result[1] == "42"

    def test_without_arg(self, cfg):
        result = NUM(config=cfg)
        assert result[0] == "regex"
        assert r"\d+" in result[1]


class TestPos:
    def test_single(self, cfg):
        result = POS("VERB", config=cfg)
        assert result == ("pos", "VERB", ExtendedOp(None))

    def test_multiple(self, cfg):
        result = POS("VERB", "NOUN", config=cfg)
        assert result[0] == "pos"
        assert result[1] == ["VERB", "NOUN"]


class TestEntity:
    def test_single(self, cfg):
        result = ENTITY("PERSON", config=cfg)
        assert result == ("entity", "PERSON", ExtendedOp(None))

    def test_multiple(self, cfg):
        result = ENTITY("PERSON", "ORG", config=cfg)
        assert result[0] == "entity"
        assert result[1] == ["PERSON", "ORG"]


class TestLemma:
    def test_basic(self, cfg):
        result = LEMMA("run", config=cfg)
        assert result == ("lemma", "run", ExtendedOp(None))


class TestPrefix:
    def test_basic(self, cfg):
        result = PREFIX("meta", config=cfg)
        assert result == ("prefix", "meta", ExtendedOp(None))


class TestInList:
    def test_basic(self, cfg):
        result = IN_LIST(["a", "b"], config=cfg)
        assert result[0] == "any_of"
        assert isinstance(result[2], ExtendedOp)


class TestAssign:
    def test_sets_variable(self, cfg):
        ASSIGN("myvar", "myval", config=cfg)
        assert cfg.get_variable("myvar") == "myval"


class TestConfigMacro:
    def test_sets_config(self, cfg):
        CONFIG("ignore_case", "N", config=cfg)
        assert cfg.ignore_case is False

    def test_sets_config_true(self, cfg):
        cfg.set_config("ignore_case", "F")
        CONFIG("ignore_case", "Y", config=cfg)
        assert cfg.ignore_case is True


class TestExec:
    def test_resolves_string(self, cfg):
        assert EXEC("hello", config=cfg) == "hello"

    def test_resolves_callable(self, cfg):
        result = EXEC(lambda config: "resolved", config=cfg)
        assert result == "resolved"


class TestPattern:
    def test_with_tuple(self, cfg):
        item = ("value", "test", ExtendedOp(None))
        result = PATTERN(item, config=cfg)
        assert isinstance(result, list)
        assert result[0] == item

    def test_with_list_wraps_nested(self, cfg):
        items = [("value", "test", ExtendedOp(None))]
        result = PATTERN(items, config=cfg)
        assert result[0][0] == "nested"


class TestNested:
    def test_basic(self, cfg):
        children = [("value", "test", ExtendedOp(None))]
        result = NESTED(children, config=cfg)
        assert result[0] == "nested"
        assert result[1] is children

    def test_with_op(self, cfg):
        result = NESTED([], config=cfg, op="+")
        assert result[2] == "+"


class TestImport:
    def test_registers_module(self, cfg):
        IMPORT("rita.modules.fuzzy", config=cfg)
        assert len(cfg.modules) == 1
