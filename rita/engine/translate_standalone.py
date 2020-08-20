import logging
import re
import json

from functools import partial
from itertools import groupby

logger = logging.getLogger(__name__)


def apply_operator(syntax, op):
    if not op:
        return syntax

    elif op == "!":  # A bit complicated one
        return (r"((?!{})\w+)".format(syntax
                                      .rstrip(")")
                                      .lstrip("(")))
    else:
        return syntax + op


def any_of_parse(lst, op=None):
    clause = r"((^|\s)(({0})\s?))".format("|".join(sorted(lst, key=lambda x: (-len(x), x))))
    return apply_operator(clause, op)


def regex_parse(r, op=None):
    initial = "(" + r + r"\s?" + ")"
    return apply_operator(initial, op)


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
    return apply_operator(r"([.,!;?:]\s?)", op)


def word_parse(value, op=None):
    initial = r"({}\s?)".format(value)
    return apply_operator(initial, op)


def fuzzy_parse(r, op=None):
    # TODO: build premutations
    return apply_operator(r"({0})[.,?;!]?".format("|".join(r)), op)


def phrase_parse(value, op=None):
    return apply_operator(r"({}\s?)".format(value), op)


PARSERS = {
    "any_of": any_of_parse,
    "value": word_parse,
    "regex": regex_parse,
    "entity": entity_parse,
    "lemma": partial(not_supported, "LEMMA"),
    "pos": partial(not_supported, "POS"),
    "punct": punct_parse,
    "fuzzy": fuzzy_parse,
    "phrase": phrase_parse,
}


def rules_to_patterns(label, data):
    logger.debug("data: {}".format(data))

    def gen():
        """
        Implicitly add spaces between rules
        """
        if len(data) == 0:
            return

        yield data[0]

        for (t, d, op) in data[1:]:
            yield t, d, op

    return (
        label,
        [PARSERS[t](d, op) for (t, d, op) in gen()],
    )


class RuleExecutor(object):
    def __init__(self, patterns, config):
        self.config = config
        self.patterns = [self.compile(label, rules)
                         for label, rules in patterns]
        self.raw_patterns = patterns

    def compile(self, label, rules):
        flags = re.DOTALL
        if self.config.ignore_case:
            flags = flags | re.IGNORECASE

        regex_str = r"(?P<{0}>{1})".format(label, "".join(rules))
        try:
            return re.compile(regex_str, flags)
        except Exception as ex:
            logger.exception("Failed to compile: '{0}', Reason: \n{1}".format(regex_str, str(ex)))
            return None

    def _results(self, text):
        for p in self.patterns:
            for match in p.finditer(text):
                yield {
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group().strip(),
                    "label": match.lastgroup,
                }

    def execute(self, text):
        results = sorted(list(self._results(text)), key=lambda x: x["start"])
        for k, g in groupby(results, lambda x: x["start"]):
            group = list(g)
            if len(group) == 1:
                yield group[0]
            else:
                data = sorted(group, key=lambda x: -x["end"])
                yield data[0]

    @staticmethod
    def load(path):
        from rita.config import SessionConfig
        config = SessionConfig()
        with open(path, "r") as f:
            patterns = [(obj["label"], obj["rules"])
                        for obj in map(json.loads, f.readlines())]
            return RuleExecutor(patterns, config)

    def save(self, path):
        with open(path, "w") as f:
            for pattern in self:
                f.write("{0}\n".format(json.dumps(pattern)))

    def __iter__(self):
        for label, rules in self.raw_patterns:
            yield {"label": label, "rules": rules}


def compile_rules(rules, config):
    logger.info("Using standalone rule implementation")
    patterns = [rules_to_patterns(*group) for group in rules]
    executor = RuleExecutor(patterns, config)
    return executor
