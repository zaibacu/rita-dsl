import pytest

from rita.config import SessionConfig
from rita.utils import ExtendedOp
from rita.modules.orth import ORTH
from rita.modules.tag import TAG, TAG_WORD


@pytest.fixture
def cfg():
    return SessionConfig()


class TestOrth:
    def test_returns_tuple_with_case_override(self, cfg):
        result = ORTH("IEEE", config=cfg)
        assert result[0] == "orth"
        assert result[1] == "IEEE"
        assert isinstance(result[2], ExtendedOp)
        assert result[2].case_sensitive_override is True

    def test_with_operator(self, cfg):
        result = ORTH("ISO", config=cfg, op="?")
        assert result[0] == "orth"
        assert result[1] == "ISO"
        assert result[2].value == "?"
        assert result[2].case_sensitive_override is True

    def test_without_operator(self, cfg):
        result = ORTH("test", config=cfg)
        assert result[2].op is None


class TestTag:
    def test_returns_tuple(self, cfg):
        result = TAG("^NN|^JJ", config=cfg)
        assert result[0] == "tag"
        assert result[1] == {"tag": "^NN|^JJ"}
        assert isinstance(result[2], ExtendedOp)

    def test_with_operator(self, cfg):
        result = TAG("^VB", config=cfg, op="+")
        assert result[2].value == "+"

    def test_tag_word_with_string(self, cfg):
        result = TAG_WORD("^VB", "proposed", config=cfg)
        assert result[0] == "tag"
        assert result[1] == {"tag": "^VB", "word": "proposed"}

    def test_tag_word_with_list(self, cfg):
        result = TAG_WORD("^VB", ["perceived", "proposed"], config=cfg)
        assert result[0] == "tag"
        assert result[1] == {"tag": "^VB", "list": ["perceived", "proposed"]}

    def test_tag_word_with_operator(self, cfg):
        result = TAG_WORD("^NN", "test", config=cfg, op="?")
        assert result[2].value == "?"


class TestPluralize:
    @pytest.fixture(autouse=True)
    def _skip_without_inflect(self):
        pytest.importorskip("inflect")

    def test_pluralizing_function(self):
        from rita.modules.pluralize import pluralizing
        result = pluralizing(["car"])
        assert "car" in result
        assert "cars" in result

    def test_pluralizing_multiple(self):
        from rita.modules.pluralize import pluralizing
        result = pluralizing(["car", "ship"])
        assert len(result) == 4
        assert "car" in result
        assert "cars" in result
        assert "ship" in result
        assert "ships" in result

    def test_pluralize_macro_single_word(self, cfg):
        from rita.modules.pluralize import PLURALIZE
        result = PLURALIZE("car", config=cfg)
        assert result[0] == "any_of"
        assert "car" in result[1]
        assert "cars" in result[1]
        assert isinstance(result[2], ExtendedOp)

    def test_pluralize_macro_list(self, cfg):
        from rita.modules.pluralize import PLURALIZE
        result = PLURALIZE(["bicycle", "ship"], config=cfg)
        assert result[0] == "any_of"
        assert "bicycle" in result[1]
        assert "bicycles" in result[1]
        assert "ship" in result[1]
        assert "ships" in result[1]


class TestNames:
    def test_two_part_name_generates_initial_variant(self, cfg):
        from rita.modules.names import NAMES
        (kind, names, op) = NAMES("John Silver", config=cfg)
        assert kind == "any_of"
        assert "John Silver" in names
        assert r"J\. Silver" in names
        assert op.case_sensitive_override is True

    def test_three_part_name_variants(self, cfg):
        from rita.modules.names import NAMES
        (_, names, _) = NAMES("John Ronald Tolkien", config=cfg)
        assert "John Ronald Tolkien" in names
        assert r"John R\. Tolkien" in names
        assert r"J\. R\. Tolkien" in names

    def test_seniority_suffix(self, cfg):
        from rita.modules.names import NAMES
        (_, names, _) = NAMES("Roy Jones junior", config=cfg)
        assert any(r"jr\." in n for n in names)

    def test_stop_names_not_trimmed(self, cfg):
        from rita.modules.names import generate_names
        variants = list(generate_names(["Juan van Damme"]))
        # "van" is a stop name and must never be turned into an initial
        assert ("Juan", "van", "Damme") not in [tuple(v) for v in variants if r"v\." in " ".join(v)]

    def test_names_match_in_standalone(self, cfg):
        import rita
        parser = rita.compile_string(
            '!IMPORT("rita.modules.names")\n'
            'NAMES("John Silver")->MARK("PERSON")',
            use_engine="standalone"
        )
        for text in ["John Silver was here", "J. Silver was here"]:
            results = list(parser.execute(text))
            assert len(results) == 1, text


class TestFuzzy:
    def test_double_letter_premutations(self, cfg):
        from rita.modules.fuzzy import premutations
        variants = list(premutations("hello"))
        assert "hello" in variants
        assert "hel{1,2}o" in variants

    def test_slang_variant(self, cfg):
        from rita.modules.fuzzy import premutations
        variants = list(premutations("you"))
        assert any("u" in v for v in variants)

    def test_fuzzy_matches_typo_in_standalone(self, cfg):
        import rita
        parser = rita.compile_string(
            '!IMPORT("rita.modules.fuzzy")\n'
            '{FUZZY("hello")}->MARK("GREETING")',
            use_engine="standalone"
        )
        assert len(list(parser.execute("helo there"))) == 1
        assert len(list(parser.execute("hello there"))) == 1
