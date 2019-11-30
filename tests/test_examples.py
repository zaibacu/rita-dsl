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
    from rita.engine.translate_standalone import compile_tree
    patterns = rita.compile(rules_path, compile_fn=compile_tree)
    def parse(text):
        results = list(patterns.execute(text))
        return list([(r["text"], r["label"]) for r in results])
    return parse


@pytest.mark.parametrize('engine', [spacy_engine])
def test_color_car(engine):
    text = """
    John Silver was driving a red car. It was BMW X6 Mclass. John likes driving it very much.
    """
    parser = engine("examples/color-car.rita")
    entities = set(parser(text))

    expected = set([
        ("John Silver", "PERSON"),       # Normal NER
        ("red car", "CAR_COLOR"),        # Our first rule
        ("BMW X6 Mclass", "CAR_MODEL"),  # Our second rule
        ("John likes driving", "LIKED_ACTION")  # Our third rule
    ])

    assert entities.issuperset(expected)


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_fuzzy_matching(engine):
    parser = engine("examples/fuzzy-matching.rita")

    # Check if we're matching with capitalized word
    t1 = """
    Squirrel just walked outside
    """

    entities = parser(t1)

    assert len(entities) == 1
    assert entities[0] == ("Squirrel", "CRITTER")

    # Check if we're matching with all CAPS
    t2 = """
    there's a SQUIRREL
    """

    entities = parser(t2)

    assert len(entities) == 1
    assert entities[0] == ("SQUIRREL", "CRITTER")

    
@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_election(engine):
    parser = engine("examples/simple-match.rita")
    text = """
    Donald Trump was elected President in 2016 defeating Hilary Clinton.
    """

    entities = set(parser(text))
    expected = set([
        ("Donald Trump was elected", "WON_ELECTION"),
        ("defeating Hilary Clinton", "LOST_ELECTION"),
    ])

    assert entities.issuperset(expected)
