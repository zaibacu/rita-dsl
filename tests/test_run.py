import sys
import json
import tempfile

import pytest
import rita

from rita.run import main
from rita.shortcuts import setup_spacy


def test_simple_compile(mocker):
    sys.argv = [
        "rita-dsl",
        "-f",
        "examples/cheap-phones.rita",
        "output.jsonl"
    ]
    main()


def test_simple_spacy_compile(mocker):
    sys.argv = [
        "rita-dsl",
        "-f",
        "examples/cheap-phones.rita",
        "--engine=spacy",
        "output.jsonl"
    ]
    main()


def test_simple_standalone_compile(mocker):
    sys.argv = [
        "rita-dsl",
        "-f",
        "examples/cheap-phones.rita",
        "--engine=standalone",
        "output.jsonl"
    ]
    main()


def test_shortcuts_spacy_inline():
    spacy = pytest.importorskip("spacy", minversion="2.1")
    nlp = spacy.load("en")
    rules = """
    {WORD("TEST")}->MARK("TEST")
    """
    setup_spacy(nlp, rules_string=rules)


def test_shortcuts_spacy_file():
    spacy = pytest.importorskip("spacy", minversion="2.1")
    nlp = spacy.load("en")
    setup_spacy(nlp, rules_path="examples/color-car.rita")


def test_shortcuts_spacy_compiled():
    spacy = pytest.importorskip("spacy", minversion="2.1")
    nlp = spacy.load("en")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl") as f:
        patterns = rita.compile("examples/color-car.rita")
        for pattern in patterns:
            f.write(json.dumps(pattern) + "\n")
        setup_spacy(nlp, patterns=f.name)


def test_shortcuts_spacy_giving_no_rules():
    spacy = pytest.importorskip("spacy", minversion="2.1")
    nlp = spacy.load("en")
    with pytest.raises(RuntimeError):
        setup_spacy(nlp)
