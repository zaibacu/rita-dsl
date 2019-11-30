import pytest
import rita


@pytest.fixture
def spacy_engine(request):
    spacy = pytest.importorskip("spacy", minversion="2.1")
    def parser(rules_path):
        patterns = rita.compile(rules_path)
        nlp = spacy.load("en")
        ruler = spacy.pipeline.EntityRuler(nlp, overwrite_ents=True)
        ruler.add_patterns(patterns)
        nlp.add_pipe(ruler)
        
        def parse(text):
            doc = nlp(text)
            return list([(e.text, e.label_) for e in doc.ents])
        return parse
    return parser


@pytest.fixture
def standalone_engine(request):
    from rita.engine.translate_standalone import compile_tree
    def parser(rules_path):
        patterns = rita.compile(rules_path, compile_fn=compile_tree)
        
        def parse(text):
            results = list(patterns.execute(text))
            return list([(r["text"], r["label"]) for r in results])
        return parse
    return parser


def test_color_car(spacy_engine):
    text = """
    John Silver was driving a red car. It was BMW X6 Mclass. John likes driving it very much.
    """
    parser = spacy_engine("examples/color-car.rita")
    entities =  parser(text)

    assert entities[0] == ("John Silver", "PERSON")  # Normal NER
    assert entities[1] == ("red car", "CAR_COLOR")  # Our first rule
    assert entities[2] == ("BMW X6 Mclass", "CAR_MODEL")  # Our second rule
    assert entities[3] == ("John likes driving", "LIKED_ACTION")  # Our third rule


def test_fuzzy_matching(spacy_engine):
    parser = spacy_engine("examples/fuzzy-matching.rita")

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


def test_standalone_simple(standalone_engine):
    parser = standalone_engine("examples/simple-match.rita")
    text = """
    Donald Trump was elected President in 2016 defeating Hilary Clinton.
    """

    entities = parser(text)
    assert entities[0] == ("Donald Trump was elected", "WON_ELECTION")
    assert entities[1] == ("defeating Hilary Clinton", "LOST_ELECTION")
