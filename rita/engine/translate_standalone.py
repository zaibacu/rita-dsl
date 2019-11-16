import logging
import re

from functools import partial

logger = logging.getLogger(__name__)


def any_of_parse(lst, op=None):
    initial = r"({0})".format("|".join(lst))
    if op:
        return initial + op

    return initial


def regex_parse(r, op=None):
    initial = r
    if op:
        return initial + op

    return initial


def not_supported(key, *args, **kwargs):
    raise RuntimeError(
        "Rule '{0}' is not supported in standalone mode"
        .format(key)
    )


def person_parse(op=None):
    initial = r"([A-Z]\w+\s?)"
    if op:
        return initial + op

    return initial


def entity_parse(value, op=None):
    if value == "PERSON":
        return person_parse(op)
    else:
        return not_supported(value)


def punct_parse():
    return r"[.,!;?:]"


def word_parse(value, op=None):
    return r"({})".format(value)


PARSERS = {
    "any_of": any_of_parse,
    "value": word_parse,
    "regex": regex_parse,
    "entity": entity_parse,
    "lemma": partial(not_supported, "LEMMA"),
    "pos": partial(not_supported, "POS"),
    "punct": punct_parse,
    "fuzzy": partial(not_supported, "FUZZY"),
}


def rules_to_patterns(rule):
    if rule:
        logger.info(rule)
        yield (
            rule["label"],
            [PARSERS[t](d, op) for (t, d, op) in rule["data"]],
        )


class RuleExecutor(object):
    def __init__(self, patterns):
        self.patterns = [self.compile(label, rules)
                         for label, rules in patterns]

    def compile(self, label, rules):
        return re.compile(r"(?P<{0}>{1})".format(label, "\s".join(rules)))

    def execute(self, text):
        for p in self.patterns:
            for match in p.finditer(text):
                yield {
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(),
                    "label": match.lastgroup,
                }


def compile_tree(root):
    logger.info("Using standalone rule implementation")
    docs = [doc for doc in root if doc]
    patterns = [p
                for doc in docs
                for p in rules_to_patterns(doc())]

    executor = RuleExecutor(patterns)
    return executor
