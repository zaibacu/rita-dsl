import logging

from functools import partial

logger = logging.getLogger(__name__)


def any_of_parse(lst, op=None):
    extra = []

    def is_simple(w):
        return not "-" in w

    # Covers basic case when all words are normal
    normalized = set(map(lambda x: x.lower(), lst))
    simple = set(filter(is_simple, normalized))
    other = normalized - simple
    
    base = {"LOWER": {"REGEX": r"({0})".format("|".join(simple))}}
    if op:
        base["OP"] = op

    if len(other) > 0:
        base["OP"] = "?"
    yield base

    # Not very good solution
    # This should be separate rules instead of single one with bunch of `?` operators

    for item in other:
        buff = item.split("-")
        yield next(generic_parse("ORTH", buff[0], "?"))
        for b in buff[1:]:
            yield next(generic_parse("ORTH", "-", "?"))
            yield next(generic_parse("ORTH", b, "?"))


def regex_parse(r, op=None):
    d = {"TEXT": {"REGEX": r}}

    if op:
        d["OP"] = op
    yield d


def fuzzy_parse(r, op=None):
    # TODO: build premutations
    d = {"LOWER": {"REGEX": "({0})[.,?;!]?".format("|".join(r))}}
    if op:
        d["OP"] = op
    yield d


def generic_parse(tag, value, op=None):
    d = {}
    d[tag] = value
    if op:
        d["OP"] = op
    yield d

def punct_parse(_, op=None):
    d = {}
    d["IS_PUNCT"] = True
    if op:
        d["OP"] = op
    yield d

PARSERS = {
    "any_of": any_of_parse,
    "value": partial(generic_parse, "ORTH"),
    "regex": regex_parse,
    "entity": partial(generic_parse, "ENT_TYPE"),
    "lemma": partial(generic_parse, "LEMMA"),
    "pos": partial(generic_parse, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
}


def rules_to_patterns(label, data):
    return {
        "label": label,
        "pattern": [p
                    for (t, d, op) in data
                    for p in PARSERS[t](d, op)],
    }


def compile_rules(rules):
    logger.info("Using spaCy rules implementation")
    return [rules_to_patterns(*group)
            for group in rules]
