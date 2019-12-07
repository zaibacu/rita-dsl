# RITA DSL

This is a language, loosely based on language [Apache UIMA RUTA](https://uima.apache.org/ruta.html), focused on writing manual language rules, which compiles into [spaCy](https://github.com/explosion/spaCy) compatible patterns. These patterns can be used for doing [manual NER](https://spacy.io/api/entityruler) as well as used in other processes, like retokenizing and pure matching

# Live Demo

[Demo Page](https://rita-demo.herokuapp.com/)

# Documentation

- [Syntax Guide](docs/syntax.md)

- [Macros](docs/macros.md)

- [Extending](docs/extend.md) - injecting custom macros to be used inside rule generation


# Quick Start
Install it via `pip install rita-dsl`

You can start defining rules by creating file with extention `*.rita`

Bellow is complete example which can be used as a reference point

```
cars = LOAD("examples/cars.txt") # Load items from file
colors = {"red", "green", "blue", "white", "black"} # Declare items inline

{IN_LIST(colors), WORD("car")} -> MARK("CAR_COLOR") # If first token is in list `colors` and second one is word `car`, label it

{IN_LIST(cars), WORD+} -> MARK("CAR_MODEL") # If first token is in list `cars` and follows by 1..N words, label it

{ENTITY("PERSON"), LEMMA("like"), WORD} -> MARK("LIKED_ACTION") # If first token is Person, followed by any word which has lemma `like`, label it
```

Now you can compile these rules `rita -f <your-file>.rita output.jsonl`

# Using compiled rules

## spaCy backend

```python
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en")
ruler = EntityRuler(nlp, overwrite_ents=True)
ruler.from_disk("output.jsonl")
nlp.add_pipe(ruler)
```

Everytime you'll parse text with spaCy, it will run usual workflow and apply these rules

```python
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
```

Alternativelly, if `rita` is used as a dependency in project and you prefer to compile rules dynamically, you can do:

```python
import rita
import spacy
from spacy.pipeline import EntityRuler

nlp = spacy.load("en")
ruler = EntityRuler(nlp, overwrite_ents=True)

patterns = rita.compile("examples/color-car.rita")

ruler.add_patterns(patterns)
nlp.add_pipe(ruler)
```

If you don't want to use file to store rules, they can be compiled directly from string

```python
patterns = rita.compile_string("""
{WORD("Hello"), WORD("World")}->MARK("GREETING")
""")
```


## Standalone Version

While it is highly recommended to use it with spaCy as a base, there can be cases when pure python regex is the only option.

You can pass rule compilation function explicitly. This concrete function will build regular expressions and create executor which accepts raw text and returns list of results.

Here's a test covering this case

```python
def test_standalone_simple():
    from rita.engine.translate_standalone import compile_rules
    patterns = rita.compile("examples/simple-match.rita", compile_fn=compile_rules)
    results = list(patterns.execute("Donald Trump was elected President in 2016 defeating Hilary Clinton."))
    assert len(results) == 2
    entities = list([(r["text"], r["label"]) for r in results])

    assert entities[0] == ("Donald Trump was elected", "WON_ELECTION")
    assert entities[1] == ("defeating Hilary Clinton", "LOST_ELECTION")
```
