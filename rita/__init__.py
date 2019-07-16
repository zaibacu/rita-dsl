import logging

from rita.translate import rules_to_patterns
from rita.parser import RitaParser

logger = logging.getLogger(__name__)


def compile(fname):
    parser = RitaParser()
    parser.build()
    with open(fname, "r") as f:
        raw = f.read()

    root = parser.parse(raw)
    logger.debug(root)
    result = [rule for doc in root if doc for rule in rules_to_patterns(doc())]
    return result
