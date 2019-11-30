import logging
import re

from functools import partial

logger = logging.getLogger(__name__)

def apply_operator(syntax, op):
    if not op:
        return syntax

    elif op == "!": # A bit complicated one
        return ("((?!{})\w+)".format(syntax
                            .rstrip(")")
                            .lstrip("(")))
    else:
        return syntax + op


def any_of_parse(lst, op=None):
    return apply_operator(r"({0})".format("|".join(lst)), op)


def regex_parse(r, op=None):
    return apply_operator(r, op)


def not_supported(key, *args, **kwargs):
    raise RuntimeError(
        "Rule '{0}' is not supported in standalone mode"
        .format(key)
    )


def person_parse(op=None):
    return apply_operator(r"([A-Z]\w+\s?)", op)


def entity_parse(value, op=None):
    if value == "PERSON":
        return person_parse(op)
    else:
        return not_supported(value)


def punct_parse(_, op=None):
    return apply_operator(r"[.,!;?:]", op)


def word_parse(value, op=None):
    if value:
        initial = r"({})".format(value)
    else:
        initial = r"(\w+)"

    return apply_operator(initial, op)

def fuzzy_parse(r, op=None):
    # TODO: build premutations
    return apply_operator(r"({0})[.,?;!]?".format("|".join(r)), op)


def whitespace_parse(_, op=None):
    return r"\s"


PARSERS = {
    "any_of": any_of_parse,
    "value": word_parse,
    "regex": regex_parse,
    "entity": entity_parse,
    "lemma": partial(not_supported, "LEMMA"),
    "pos": partial(not_supported, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
    "whitespace": whitespace_parse,
}


def rules_to_patterns(label, data):
    logger.debug("data: {}".format(data))
    def gen():
        """
        Implicitly add spaces between rules
        """
        yield data[0]
        for (t, d, op) in data[1:]:
            if t != "punct":
                yield ("whitespace", None, None) 
            yield (t, d, op)
    
    return (
        label,
        [PARSERS[t](d, op) for (t, d, op) in gen()],
    )


class RuleExecutor(object):
    def __init__(self, patterns):
        self.patterns = [self.compile(label, rules)
                         for label, rules in patterns]

    def compile(self, label, rules):
        return re.compile(r"(?P<{0}>{1})".format(label, "".join(rules)), re.IGNORECASE)

    def execute(self, text):
        for p in self.patterns:
            for match in p.finditer(text):
                yield {
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(),
                    "label": match.lastgroup,
                }


def compile_rules(rules):
    logger.info("Using standalone rule implementation")
    patterns = [rules_to_patterns(*group) for group in rules]
    executor = RuleExecutor(patterns)
    return executor
