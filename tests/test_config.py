import pytest

from rita.config import with_config, SessionConfig


@pytest.fixture
def cfg():
    return SessionConfig()


@with_config
def test_config_decorator(config):
    assert config


def test_registered_engines(cfg):
    assert len(cfg.available_engines) > 0


def test_registered_engines_has_spacy(cfg):
    pytest.importorskip("spacy", minversion="2.1")
    from rita.engine.translate_spacy import compile_rules
    assert len(cfg.available_engines) == 3
    assert cfg.default_engine == compile_rules


def test_default_values(cfg):
    assert cfg.ignore_case
    assert cfg.implicit_punct
    assert not cfg.implicit_hyphon

    cfg.ignore_case = False
    assert not cfg.ignore_case

    cfg.implicit_punct = False
    assert not cfg.implicit_punct

    cfg.implicit_hyphon = True
    assert cfg.implicit_hyphon


def test_register_module(cfg):
    cfg.register_module("rita.modules.fuzzy")

    assert len(cfg.modules) == 1


def test_set_config_true_values(cfg):
    for v in ["1", "T", "Y"]:
        cfg.set_config("ignore_case", "F")
        cfg.set_config("ignore_case", v)
        assert cfg.ignore_case is True


def test_set_config_false_values(cfg):
    for v in ["0", "F", "N"]:
        cfg.set_config("ignore_case", "T")
        cfg.set_config("ignore_case", v)
        assert cfg.ignore_case is False


def test_set_config_string_value(cfg):
    cfg.set_config("custom_key", "custom_value")
    assert cfg.custom_key == "custom_value"


def test_set_variable_and_get(cfg):
    cfg.set_variable("myvar", [1, 2, 3])
    assert cfg.get_variable("myvar") == [1, 2, 3]


def test_set_engine(cfg):
    from rita.engine.translate_standalone import compile_rules as standalone_engine
    result = cfg.set_engine("standalone")
    assert result == standalone_engine


def test_list_branching_standalone(cfg):
    cfg.set_engine("standalone")
    assert cfg.list_branching is False


def test_new_nested_group_id(cfg):
    id1 = cfg.new_nested_group_id()
    id2 = cfg.new_nested_group_id()
    assert id2 == id1 + 1


def test_session_config_getattr_delegation(cfg):
    # available_engines is on root Config, not SessionConfig
    assert hasattr(cfg, "available_engines")
    assert len(cfg.available_engines) > 0
