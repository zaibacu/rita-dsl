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
    spacy = pytest.importorskip("spacy", minversion="2.1")
    from rita.engine.translate_spacy import compile_rules
    assert len(cfg.available_engines) == 2
    assert cfg.default_engine == compile_rules


def test_default_values(cfg):
    assert cfg.list_ignore_case
    assert cfg.implicit_punct

    cfg.list_ignore_case = False
    assert not cfg.list_ignore_case

    cfg.implicit_punct = False
    assert not cfg.implicit_punct

def test_register_module(cfg):
    cfg.register_module("rita.modules.fuzzy")

    assert len(cfg.modules) == 1
