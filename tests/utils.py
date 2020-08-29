import re

import pytest
import rita


def load_rules(rules_path):
    with open(rules_path, "r") as f:
        return f.read()


def spacy_engine(rules, **kwargs):
    spacy = pytest.importorskip("spacy", minversion="2.1")
    patterns = rita.compile_string(rules, **kwargs)
    nlp = spacy.load("en")
    ruler = spacy.pipeline.EntityRuler(nlp, overwrite_ents=True)
    print(patterns)
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    def parse(text):
        doc = nlp(text)
        return list([(e.text, e.label_) for e in doc.ents])
    return parse


def standalone_engine(rules, **kwargs):
    parser = rita.compile_string(rules, use_engine="standalone", **kwargs)
    print(parser.patterns)

    def parse(text):
        results = list(parser.execute(text))
        return list([(r["text"], r["label"]) for r in results])
    return parse


def rust_engine(rules, **kwargs):
    from rita.engine.translate_rust import load_lib
    lib = load_lib()
    if lib is None:
        pytest.skip("Missing rita-rust dynamic lib, skipping related tests")
    print("Trying to run: {}".format(rules))
    parser = rita.compile_string(rules, use_engine="rust", **kwargs)
    print(parser.patterns)

    def parse(text):
        results = list(parser.execute(text))
        return list([(r["text"], r["label"]) for r in results])
    return parse


def normalize_output(r):
    return re.sub(r"\s+", " ", r.strip().replace("\n", ""))


def raw_compare(r1, r2):
    r1 = normalize_output(r1)
    r2 = normalize_output(r2)

    assert r1 == r2
