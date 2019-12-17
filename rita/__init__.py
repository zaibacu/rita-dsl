import logging
import types

from rita.config import with_config
from rita.parser import RitaParser
from rita.preprocess import preprocess_rules


logger = logging.getLogger(__name__)

__version__ = (0, 3, 2)


def get_version():
    return "{0}.{1}.{2}".format(__version__)


@with_config
def compile_string(raw, config, use_engine=None):
    parser = RitaParser(config)
    parser.build()
    root = parser.parse(raw)
    logger.debug(root)
    if use_engine:
        compile_rules = config.get_engine(use_engine)
    else:
        compile_rules = config.default_engine
    rules = list(preprocess_rules(root, config))
    result = compile_rules(rules, config)
    if isinstance(result, types.GeneratorType):
        return list(result)
    else:
        return result


def compile(fname, compile_fn=None):
    with open(fname, "r") as f:
        raw = f.read()

    return compile_string(raw, compile_fn)
