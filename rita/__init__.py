from rita.translate import rules_to_patterns
from rita.parser import RitaParser


def compile(fname):
    parser = RitaParser()
    parser.build()
    with open(fname, "r") as f:
        raw = f.read()

    root = parser.parse(raw)
    result = [rules_to_patterns(doc())
              for doc in root
              if doc]
    return result
