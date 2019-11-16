import logging

from rita import engine
from rita.parser import RitaParser

logger = logging.getLogger(__name__)


def compile_string(raw):
    parser = RitaParser()
    parser.build()
    root = parser.parse(raw)
    logger.debug(root)
    compile_tree = engine.get_default()
    return list(compile_tree(root))


def compile(fname):
    with open(fname, "r") as f:
        raw = f.read()

    return compile_string(raw)
