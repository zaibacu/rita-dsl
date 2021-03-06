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
