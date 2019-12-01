import pytest
import rita


def spacy_engine(rules_path):
    spacy = pytest.importorskip("spacy", minversion="2.1")
    patterns = rita.compile(rules_path)
    nlp = spacy.load("en")
    ruler = spacy.pipeline.EntityRuler(nlp, overwrite_ents=True)
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    
    def parse(text):
        doc = nlp(text)
        return list([(e.text, e.label_) for e in doc.ents])
    return parse


def standalone_engine(rules_path):
    from rita.engine.translate_standalone import compile_rules
    parser = rita.compile(rules_path, compile_fn=compile_rules)
    print(parser.patterns)
    def parse(text):
        results = list(parser.execute(text))
        return list([(r["text"], r["label"]) for r in results])
    return parse
