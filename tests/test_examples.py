import pytest
import rita


def test_color_car():
    spacy = pytest.importorskip("spacy", minversion="2.1")

    patterns = rita.compile("examples/color-car.rita")
    print(patterns)
    assert len(patterns) == 3

    # Build Spacy
    nlp = spacy.load("en")
    ruler = spacy.pipeline.EntityRuler(nlp, overwrite_ents=True)
    ruler.add_patterns(patterns)

    nlp.add_pipe(ruler)

    # Load example

    text = """
    John Silver was driving a red car. It was BMW X6 Mclass. John likes driving it very much.
    """

    doc = nlp(text)

    entities = [(e.text, e.label_) for e in doc.ents]
    print(entities)

    assert entities[0] == ("John Silver", "PERSON")  # Normal NER
    assert entities[1] == ("red car", "CAR_COLOR")  # Our first rule
    assert entities[2] == ("BMW X6 Mclass", "CAR_MODEL")  # Our second rule
    assert entities[3] == ("John likes driving", "LIKED_ACTION")  # Our third rule


def test_fuzzy_matching():
    spacy = pytest.importorskip("spacy", minversion="2.1")

    patterns = rita.compile("examples/fuzzy-matching.rita")
    print(patterns)
    assert len(patterns) == 1

    # Build Spacy
    nlp = spacy.load("en")
    ruler = spacy.pipeline.EntityRuler(nlp, overwrite_ents=True)
    ruler.add_patterns(patterns)

    nlp.add_pipe(ruler)

    # Check if we're matching with capitalized word

    t1 = """
    Squirrel just walked outside
    """

    doc = nlp(t1)

    entities = [(e.text, e.label_) for e in doc.ents]

    assert len(entities) == 1
    assert entities[0] == ("Squirrel", "CRITTER")

    # Check if we're matching with all CAPS

    t2 = """
    there's a SQUIRREL
    """

    doc = nlp(t2)

    entities = [(e.text, e.label_) for e in doc.ents]

    assert len(entities) == 1
    assert entities[0] == ("SQUIRREL", "CRITTER")

def test_standalone_simple():
    pass
