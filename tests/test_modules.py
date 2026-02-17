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
