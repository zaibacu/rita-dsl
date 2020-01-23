import os

import logging
import types

from rita.config import with_config
from rita.preprocess import preprocess_rules


logger = logging.getLogger(__name__)

__version__ = (0, 3, 4, os.getenv("VERSION_PATCH"))


def get_version():
    normalized = list([i for i in __version__ if i is not None])
    if len(normalized) == 4:
        return "{0}.{1}.{2}-{3}".format(*normalized)
    else:
        return "{0}.{1}.{2}".format(*normalized)


@with_config
def compile_string(raw, config, use_engine=None):
    from rita.parser import RitaParser
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

    return compile_string(raw)
