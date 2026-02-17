import pytest

from rita.config import SessionConfig
from rita.utils import ExtendedOp
from rita.engine.translate_spacy import (
    any_of_parse,
    regex_parse,
    fuzzy_parse,
    generic_parse,
    entity_parse,
    punct_parse,
    any_parse,
    phrase_parse,
    tag_parse,
    orth_parse,
    rules_to_patterns,
    compile_rules,
)


@pytest.fixture
def cfg():
    return SessionConfig()


@pytest.fixture
def cfg_case_sensitive():
    c = SessionConfig()
    c.set_config("ignore_case", "F")
    return c


@pytest.fixture
def empty_op():
    return ExtendedOp(None)


@pytest.fixture
def plus_op():
    return ExtendedOp("+")


@pytest.fixture
def case_sensitive_op():
    op = ExtendedOp(None)
    op.case_sensitive_override = True
    return op


class TestAnyOfParse:
    def test_ignore_case(self, cfg, empty_op):
        result = list(any_of_parse(["Apple", "Banana"], cfg, empty_op))
        assert len(result) == 1
        assert result[0] == {"LOWER": {"IN": ["apple", "banana"]}}

    def test_case_sensitive(self, cfg_case_sensitive, case_sensitive_op):
        result = list(any_of_parse(["Apple", "Banana"], cfg_case_sensitive, case_sensitive_op))
        assert len(result) == 1
        assert result[0] == {"LOWER": {"IN": ["Apple", "Banana"]}}

    def test_with_operator(self, cfg, plus_op):
        result = list(any_of_parse(["a", "b"], cfg, plus_op))
        assert result[0]["OP"] == "+"


class TestRegexParse:
    def test_ignore_case(self, cfg, empty_op):
        result = list(regex_parse(r"\d+", cfg, empty_op))
        assert result[0] == {"LOWER": {"REGEX": r"\d+"}}

    def test_case_sensitive(self, cfg_case_sensitive, case_sensitive_op):
        result = list(regex_parse(r"[A-Z]+", cfg_case_sensitive, case_sensitive_op))
        assert result[0] == {"TEXT": {"REGEX": r"[A-Z]+"}}

    def test_with_operator(self, cfg, plus_op):
        result = list(regex_parse(r"\d+", cfg, plus_op))
        assert result[0]["OP"] == "+"


class TestFuzzyParse:
    def test_basic(self, cfg, empty_op):
        result = list(fuzzy_parse(["squirrel", "squirre1"], cfg, empty_op))
        assert len(result) == 1
        assert "REGEX" in result[0]["LOWER"]
        assert "squirrel" in result[0]["LOWER"]["REGEX"]
        assert "squirre1" in result[0]["LOWER"]["REGEX"]

    def test_with_operator(self, cfg, plus_op):
        result = list(fuzzy_parse(["test"], cfg, plus_op))
        assert result[0]["OP"] == "+"


class TestGenericParse:
    def test_single_value(self, cfg, empty_op):
        result = list(generic_parse("POS", "VERB", cfg, empty_op))
        assert result[0] == {"POS": "VERB"}

    def test_list_value(self, cfg, empty_op):
        result = list(generic_parse("POS", ["VERB", "NOUN"], cfg, empty_op))
        assert result[0] == {"POS": {"IN": ["VERB", "NOUN"]}}

    def test_single_item_list(self, cfg, empty_op):
        result = list(generic_parse("POS", ["VERB"], cfg, empty_op))
        assert result[0] == {"POS": ["VERB"]}

    def test_with_operator(self, cfg, plus_op):
        result = list(generic_parse("POS", "VERB", cfg, plus_op))
        assert result[0]["OP"] == "+"


class TestEntityParse:
    def test_default_op(self, cfg, empty_op):
        result = list(entity_parse("PERSON", cfg, empty_op))
        assert result[0] == {"ENT_TYPE": "PERSON", "OP": "+"}

    def test_override_op(self, cfg):
        op = ExtendedOp("*")
        result = list(entity_parse("PERSON", cfg, op))
        assert result[0] == {"ENT_TYPE": "PERSON", "OP": "*"}


class TestPunctParse:
    def test_basic(self, cfg, empty_op):
        result = list(punct_parse(None, cfg, empty_op))
        assert result[0] == {"IS_PUNCT": True}

    def test_with_operator(self, cfg):
        op = ExtendedOp("?")
        result = list(punct_parse(None, cfg, op))
        assert result[0] == {"IS_PUNCT": True, "OP": "?"}


class TestAnyParse:
    def test_basic(self, cfg, empty_op):
        result = list(any_parse(None, cfg, empty_op))
        assert result[0] == {}

    def test_with_operator(self, cfg, plus_op):
        result = list(any_parse(None, cfg, plus_op))
        assert result[0] == {"OP": "+"}


class TestPhraseParse:
    def test_with_dash(self, cfg, empty_op):
        result = list(phrase_parse("knee-length", cfg, empty_op))
        assert len(result) == 3
        assert result[0] == {"LOWER": "knee"}
        assert result[1] == {"LOWER": "-"}
        assert result[2] == {"LOWER": "length"}

    def test_with_space(self, cfg, empty_op):
        result = list(phrase_parse("hello world", cfg, empty_op))
        assert len(result) == 2
        assert result[0] == {"LOWER": "hello"}
        assert result[1] == {"LOWER": "world"}

    def test_single_word(self, cfg, empty_op):
        result = list(phrase_parse("hello", cfg, empty_op))
        assert len(result) == 1
        assert result[0] == {"LOWER": "hello"}


class TestTagParse:
    def test_basic(self, cfg, empty_op):
        result = list(tag_parse({"tag": "^NN|^JJ"}, cfg, empty_op))
        assert result[0] == {"TAG": {"REGEX": "^NN|^JJ"}}

    def test_with_word_ignore_case(self, cfg, empty_op):
        result = list(tag_parse({"tag": "^VB", "word": "Proposed"}, cfg, empty_op))
        assert result[0]["TAG"] == {"REGEX": "^VB"}
        assert result[0]["LOWER"] == "proposed"

    def test_with_word_case_sensitive(self, cfg_case_sensitive, case_sensitive_op):
        result = list(tag_parse({"tag": "^VB", "word": "Proposed"}, cfg_case_sensitive, case_sensitive_op))
        assert result[0]["TEXT"] == "Proposed"

    def test_with_list_ignore_case(self, cfg, empty_op):
        result = list(tag_parse({"tag": "^VB", "list": ["perceived", "proposed"]}, cfg, empty_op))
        assert result[0]["TAG"] == {"REGEX": "^VB"}
        assert "REGEX" in result[0]["LOWER"]

    def test_with_list_case_sensitive(self, cfg_case_sensitive, case_sensitive_op):
        result = list(tag_parse({"tag": "^VB", "list": ["perceived", "proposed"]}, cfg_case_sensitive, case_sensitive_op))
        assert "TEXT" in result[0]

    def test_with_operator(self, cfg, plus_op):
        result = list(tag_parse({"tag": "^NN"}, cfg, plus_op))
        assert result[0]["OP"] == "+"


class TestOrthParse:
    def test_ignore_case(self, cfg, empty_op):
        result = list(orth_parse("Hello", cfg, empty_op))
        assert result[0] == {"LOWER": "hello"}

    def test_case_sensitive(self, cfg, case_sensitive_op):
        result = list(orth_parse("Hello", cfg, case_sensitive_op))
        assert result[0] == {"ORTH": "Hello"}

    def test_with_operator(self, cfg):
        op = ExtendedOp("?")
        result = list(orth_parse("test", cfg, op))
        assert result[0] == {"LOWER": "test", "OP": "?"}


class TestRulesToPatterns:
    def test_basic(self, cfg):
        data = [("value", "hello", ExtendedOp(None))]
        result = rules_to_patterns("TEST", data, cfg)
        assert result["label"] == "TEST"
        assert len(result["pattern"]) == 1
        assert result["pattern"][0] == {"LOWER": "hello"}


class TestCompileRules:
    def test_basic(self, cfg):
        rules = [("LABEL", [("value", "hello", ExtendedOp(None))])]
        result = compile_rules(rules, cfg)
        assert len(result) == 1
        assert result[0]["label"] == "LABEL"
        assert result[0]["pattern"] == [{"LOWER": "hello"}]

    def test_multiple_rules(self, cfg):
        rules = [
            ("LABEL1", [("value", "hello", ExtendedOp(None))]),
            ("LABEL2", [("punct", None, ExtendedOp(None))]),
        ]
        result = compile_rules(rules, cfg)
        assert len(result) == 2
        assert result[0]["label"] == "LABEL1"
        assert result[1]["label"] == "LABEL2"
