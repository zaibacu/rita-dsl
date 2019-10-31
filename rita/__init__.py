import logging

from rita.translate import rules_to_patterns
from rita.parser import RitaParser

logger = logging.getLogger(__name__)


def compile_string(raw):
    parser = RitaParser()
    parser.build()
    root = parser.parse(raw)
    logger.debug(root)
    result = [rule for doc in root if doc for rule in rules_to_patterns(doc())]
    return result


def compile(fname):
    with open(fname, "r") as f:
        raw = f.read()

    return compile_string(raw)
