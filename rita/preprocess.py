import logging

import rita

from functools import reduce

logger = logging.getLogger(__name__)


def add_implicit_punct(rules):
    """
    When writing rule, user usually doesn't care about some punct characters between words.
    We add them implicitly (unless this setting is turned off)
    """
    for group_label, pattern in rules:
        print("Group: {0} Pattern: {1}".format(group_label, pattern))
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

    pipeline = [dummy]

    if conf.implicit_punct:
        logger.info("Adding implicit Punctuations")
        pipeline.append(add_implicit_punct)

    return reduce(lambda acc, p: p(acc), pipeline, rules)
