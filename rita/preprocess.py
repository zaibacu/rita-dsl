import logging

import rita

from functools import reduce
from itertools import zip_longest

from rita.utils import Node

logger = logging.getLogger(__name__)


def add_implicit_punct(rules):
    """
    When writing rule, user usually doesn't care about some punct characters between words.
    We add them implicitly (unless this setting is turned off)
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                yield p
                yield ("punct", None, "?")

        if len(pattern) == 1:
            yield (group_label, pattern)
        else:
            yield (group_label, list(gen())[:-1])


def handle_multi_word(rules):
    """
    spaCy splits everything in tokens. Words with dash ends up in different tokens.
    We don't want for user to even care about this, so we make this work implicitly
    
    WORD("Knee-length") => WORD("Knee"), WORD("-"), WORD("length")
    """
    for group_label, pattern in rules:
        yield (group_label, pattern)


def branch_pattern(pattern):
    """
    Creates multiple lists for each possible permutation
    """
    root = Node()
    current = root
    for idx, p in enumerate(pattern):
        if p[0] == "either":
            for e in p[1]:
                values = e(context=[])
                for v in values:
                    current.add_child(v)
        else:
            n = Node(p)
            current.add_next(n)
            current = n

    for p in root.unwrap():
        yield p


def handle_rule_branching(rules):
    """
    If we have an OR statement, eg. `WORD(w1)|WORD(w2)`,
    Generic approach is to clone rules and use w1 in one, w2 in other.
    It may be an overkill, but some situations are not covered in simple approach
    """
    for group_label, pattern in rules:
        if any([p == "either"
                for (p, _, _) in pattern]):
            for p in branch_pattern(pattern):
                yield (group_label, p)
        else:
            yield (group_label, pattern)


def dummy(rules):
    """
    Placeholder which does nothing
    """
    return rules


def rule_tuple(d):
    return (d["label"], d["data"])


def preprocess_rules(root):
    logger.info("Preprocessing rules")
    conf = rita.config()

    rules = [rule_tuple(doc())
             for doc in root
             if doc and doc()]

    pipeline = [dummy, handle_rule_branching, handle_multi_word]

    if conf.implicit_punct:
        logger.info("Adding implicit Punctuations")
        pipeline.append(add_implicit_punct)

    return reduce(lambda acc, p: p(acc), pipeline, rules)
