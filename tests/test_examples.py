import spacy

import rita

from spacy.pipeline import EntityRuler
from rita.translate import context_to_patterns


def test_color_car():
    result = rita.compile('examples/color-car.rita')
    print(result)
    assert len(result) == 2

    patterns = context_to_patterns(result)
    print(patterns)

    # Inject into actual Spacy
    nlp = spacy.load('en')
    ruler = EntityRuler(nlp, overwrite_ents=True)
    ruler.add_patterns(patterns)
    
    nlp.add_pipe(ruler)

    # Parse text with spacy

    text = '''
    I saw a red car passing by. It was BMW X6.
    '''
    doc = nlp(text)
    ents = [(e.text, e.label_,) for e in doc.ents]
    print(ents)
    assert ents[0] == ('red car', 'CAR_COLOR')
    assert ents[1] == ('BMW X6', 'CAR_MODEL')    

    
