import logging

from functools import partial

logger = logging.getLogger(__name__)


def any_of_parse(lst, op=None):
    pass


def regex_parse(r, op=None):
    pass


def fuzzy_parse(r, op=None):
    pass


def generic_parse(tag, value, op=None):
    pass


def not_supported(key, *args, **kwargs):
    pass


PARSERS = {
    "any_of": any_of_parse,
    "value": partial(generic_parse, "ORTH"),
    "regex": regex_parse,
    "entity": partial(not_supported, "ENT_TYPE"),
    "lemma": partial(not_supported, "LEMMA"),
    "pos": partial(not_supported, "POS"),
    "punct": partial(generic_parse, "PUNCT"),
    "fuzzy": fuzzy_parse,
}


def rules_to_patterns(rule):
    if rule:
        logger.info(rule)
        yield {
            "label": rule["label"],
            "pattern": [PARSERS[t](d, op) for (t, d, op) in rule["data"]],
        }

def compile_tree(root):
    pass

