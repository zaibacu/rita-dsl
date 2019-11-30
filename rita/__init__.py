import logging
import types

from rita import engine
from rita.config import Config
from rita.parser import RitaParser
from rita.preprocess import preprocess_rules


logger = logging.getLogger(__name__)


def config():
    return Config()


def compile_string(raw, compile_fn=None):
    parser = RitaParser()
    parser.build()
    root = parser.parse(raw)
    logger.debug(root)
    if compile_fn:
        compile_rules = compile_fn
    else:
        compile_rules = engine.get_default()

    rules = list(preprocess_rules(root))
    result = compile_rules(rules)
    if isinstance(result, types.GeneratorType):
        return list(result)
    else:
        return result


def compile(fname, compile_fn=None):
    with open(fname, "r") as f:
        raw = f.read()

    return compile_string(raw, compile_fn)
