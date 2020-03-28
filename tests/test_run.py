import os
import sys
import json
import tempfile

import pytest
import rita

from rita.run import main
from rita.shortcuts import setup_spacy


def test_help(mocker):
    sys.argv = [
        "rita-dsl"
        "--help"
    ]


def test_debug(mocker):
    sys.argv = [
        "rita-dsl"
        "--debug"
    ]


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
    tmp = tempfile.NamedTemporaryFile(mode="w", encoding="UTF-8", suffix=".jsonl", delete=False)
    patterns = rita.compile("examples/color-car.rita")
    for pattern in patterns:
        tmp.write(json.dumps(pattern) + "\n")
    tmp.flush()
    tmp.close()
    setup_spacy(nlp, patterns=tmp.name)
    os.unlink(tmp.name)


def test_shortcuts_spacy_giving_no_rules():
    spacy = pytest.importorskip("spacy", minversion="2.1")
    nlp = spacy.load("en")
    with pytest.raises(RuntimeError):
        setup_spacy(nlp)
