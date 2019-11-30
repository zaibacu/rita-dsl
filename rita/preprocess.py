import logging

import rita

from functools import reduce

logger = logging.getLogger(__name__)


def add_implicit_punct(rules):
    """
    When writing rule, user usually doesn't care about some punct characters between words.
    We add them implicitly (unless this setting is turned off)
    """
    return rules


def handle_multi_word(rules):
    """
    spaCy splits everything in tokens. Words with dash ends up in different tokens.
    We don't want for user to even care about this, so we make this work implicitly
    
    WORD("Knee-length") => WORD("Knee"), WORD("-"), WORD("length")
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

    pipeline = [handle_multi_word]

    if conf.implicit_punct:
        logger.info("Adding implicit Punctuations")
        pipeline.append(add_implicit_punct)

    return reduce(lambda acc, p: p(acc), pipeline, rules)
