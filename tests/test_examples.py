import spacy

import rita

from spacy.pipeline import EntityRuler


def test_color_car():
    patterns = rita.compile("examples/color-car.rita")
    print(patterns)
    assert len(patterns) == 3

    # Build Spacy
    nlp = spacy.load("en")
    ruler = EntityRuler(nlp, overwrite_ents=True)
    ruler.add_patterns(patterns)

    nlp.add_pipe(ruler)

    # Load example

    text = """
    Johny Silver was driving a red car. It was BMW X6 Mclass. Johny likes driving it very much.
    """

    doc = nlp(text)

    entities = [(e.text, e.label_) for e in doc.ents]
    print(entities)

    assert entities[0] == ("Johny Silver", "PERSON")  # Normal NER
    assert entities[1] == ("red car", "CAR_COLOR")  # Our first rule
    assert entities[2] == ("BMW X6 Mclass", "CAR_MODEL")  # Our second rule
    assert entities[3] == ("Johny likes driving", "LIKED_ACTION")  # Our third rule
