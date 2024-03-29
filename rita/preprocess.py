import logging

from functools import reduce
from typing import Any, Mapping, Callable, List

from rita.utils import Node, deaccent, ExtendedOp
from rita.types import RuleGroup, Rules
from rita.config import SessionConfig

logger = logging.getLogger(__name__)

Pipeline = Callable[[Rules, "SessionConfig"], Rules]


def handle_prefix(rules: Rules, config: SessionConfig):
    """
    If we have a prefix and rule following it, we apply this prefix on that rule
    """
    def apply_prefix(pattern, prefix):
        (name, args, op) = pattern
        if name == "any_of":
            return (name, list(["{0}{1}".format(prefix, item)
                                for item in args]), op)
        elif name == "value":
            return name, "{0}{1}".format(prefix, args), op
        else:
            logger.warning("Don't know how to apply prefix on: {}".format(name))
            return pattern

    def gen():
        prefix = None
        for p in pattern:
            (name, args, op) = p
            if name == "prefix":
                prefix = args
            else:
                if prefix:
                    yield apply_prefix(p, prefix)
                    prefix = None
                else:
                    yield p
    for group_label, pattern in rules:
        yield group_label, list(gen())


def handle_deaccent(rules: Rules, config: SessionConfig):
    """
    If we get accented word, eg: {WORD("naïve"), WORD("bayes")}
    In case of word, it should become list => {IN_LIST({"naïve", "naive"}), WORD("bayes")}
    In case of list, it should extend list with extra items for accented and not accented versions
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                (name, args, op) = p
                if name == "value":
                    (v1, v2) = (args, deaccent(args))
                    if v1 != v2:
                        yield "any_of", (v1, v2,), op
                    else:
                        yield p
                elif name == "any_of":
                    def items():
                        for w in args:
                            (v1, v2) = (w, deaccent(w))
                            if v1 != v2:
                                yield v1
                                yield v2
                            else:
                                yield v1

                    yield "any_of", list(items()), op
                else:
                    yield p

        yield group_label, list(gen())


def add_implicit_punct(rules: Rules, config: SessionConfig):
    """
    When writing rule,
    user usually doesn't care about some punct characters between words.
    We add them implicitly (unless this setting is turned off)
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                yield p
                yield "punct", None, ExtendedOp("?")

        if len(pattern) == 1:
            yield group_label, pattern
        else:
            yield group_label, list(gen())[:-1]


def add_implicit_hyphon(rules: Rules, config: SessionConfig):
    """
    When writing rule,
    user usually doesn't care about hyphon characters - between words.
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                yield p
                yield "value", "-", ExtendedOp("?")

        if len(pattern) == 1:
            yield group_label, pattern
        else:
            yield group_label, list(gen())[:-1]


def handle_multi_word(rules: Rules, config: SessionConfig):
    """
    spaCy splits everything in tokens.
    Words with dash ends up in different tokens.

    We don't want for user to even care about this,
    so we make this work implicitly

    WORD("Knee-length") => WORD("Knee"), WORD("-"), WORD("length")
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                (name, args, op) = p
                if name == "value" and is_complex(args):
                    yield "phrase", args, op
                else:
                    yield p

        yield group_label, list(gen())


def is_complex(arg: str) -> bool:
    # if we want to use `-` as a word
    if arg.strip() == "-":
        return False

    splitters = ["-", " "]
    return any([s in arg
                for s in splitters])


def has_complex(args: List[str]) -> bool:
    """
    Tells if any of arguments will be impacted by tokenizer
    """
    return any([is_complex(a)
                for a in args])


def branch_pattern(pattern, config: SessionConfig):
    """
    Creates multiple lists for each possible permutation
    """
    root = Node()
    current = root
    depth = 0
    for idx, p in enumerate(pattern):
        if p[0] == "either":
            n = Node()
            current.add_next(n)
            current = n
            current.depth = depth
            for e in p[1]:
                current.add_child(e(config=config))
                depth += 1
        elif p[0] == "any_of" and has_complex(p[1]):
            _all = set(p[1])
            _complex = set(filter(is_complex, _all))
            simple = _all - _complex
            n = Node()
            current.add_next(n)
            current = n
            current.depth = depth
            if len(simple) > 0:
                current.add_child(("any_of", simple, p[2]))
            for c in sorted(_complex):
                current.add_child(("phrase", c, p[2]))
                depth += 1
        else:
            n = Node(p)
            current.add_next(n)
            current = n
            current.depth = depth

    for p in root.unwrap():
        yield p


def handle_rule_branching(rules: Rules, config: SessionConfig):
    """
    If we have an OR statement, eg. `WORD(w1)|WORD(w2)`,
    Generic approach is to clone rules and use w1 in one, w2 in other.
    It may be an overkill, but some situations are not covered
    with simple approach
    """
    for group_label, pattern in rules:
        # Covering WORD(w1)|WORD(w2) case
        if any([p == "either"
                for (p, _, _) in pattern]):
            for p in branch_pattern(pattern, config):
                yield group_label, p

        # Covering case when there are complex items in list
        elif config.list_branching and any([p == "any_of" and has_complex(o)
                                            for (p, o, _) in pattern]):
            for p in branch_pattern(pattern, config):
                yield group_label, p
        else:
            yield group_label, pattern


def dummy(rules: Rules, config: SessionConfig):
    """
    Placeholder which does nothing
    """
    logger.debug("Initial rules: {}".format(rules))
    return rules


def rule_tuple(d: Mapping[str, Any]) -> RuleGroup:
    return d["label"], d["data"]


def expand_patterns(rules: Rules, config: SessionConfig):
    """
    We can have situations where inside pattern we have another pattern (via Variable).
    We want to expand this inner pattern and prepend to outer pattern
    """
    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                if type(p) is tuple:
                    (k, other, op) = p
                    if k == "nested":
                        fn = other[0][0]
                        children = other[0][1]
                        yield fn, children, op
                    else:
                        yield p
                else:
                    yield p

        yield group_label, list(gen())


def flatten_2nd_level_nested(rules: Rules, config: SessionConfig):
    """
    1st level of nested: use PATTERN(...) inside of your rule
    2nd level of nested: use PATTERN(...) which has PATTERN(...) and so on (recursively)

    we want to resolve up to 1st level
    """

    for group_label, pattern in rules:
        def gen():
            for p in pattern:
                if type(p) is list:
                    for item in p:
                        yield item
                else:
                    yield p

        yield group_label, list(gen())


def preprocess_rules(root, config: SessionConfig) -> Rules:
    logger.info("Preprocessing rules")

    rules = [rule_tuple(doc())
             for doc in root
             if doc and doc()]

    pipeline = [
        dummy,
        expand_patterns,
        handle_deaccent,
        handle_rule_branching,
        flatten_2nd_level_nested,
        handle_multi_word,
        handle_prefix
    ]

    if config.implicit_hyphon:
        logger.info("Adding implicit Hyphons")
        pipeline.append(add_implicit_hyphon)
    elif config.implicit_punct:
        logger.info("Adding implicit Punctuations")
        pipeline.append(add_implicit_punct)

    return reduce(lambda acc, p: p(acc, config), pipeline, rules)
