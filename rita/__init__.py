import os

import logging
import types

from rita.config import with_config
from rita.preprocess import preprocess_rules
from rita.precompile import precompile
from rita.utils import timer, Timer


logger = logging.getLogger(__name__)

__version__ = (0, 6, 11, os.getenv("VERSION_PATCH"))


def get_version():
    normalized = list([i for i in __version__ if i is not None])
    if len(normalized) == 4:
        return "{0}.{1}.{2}-{3}".format(*normalized)
    else:
        return "{0}.{1}.{2}".format(*normalized)


@with_config
def compile_string(raw, config, use_engine=None, **kwargs):
    from rita.parser import RitaParser
    t = Timer("Compilation")
    for k, v in kwargs.items():
        config.set_variable(k, v)

    with timer("Parsing"):
        parser = RitaParser(config)
        parser.build()
        root = parser.parse(precompile(raw))

    logger.debug(root)
    if use_engine:
        compile_rules = config.set_engine(use_engine)
    else:
        compile_rules = config.default_engine

    with timer("Preprocessing"):
        rules = list(preprocess_rules(root, config))

    with timer("Compiling"):
        result = compile_rules(rules, config, **kwargs)

    if isinstance(result, types.GeneratorType):
        patterns = list(result)
        t.stop(debug=False)
        return patterns
    else:
        t.stop(debug=False)
        return result


def compile(fname, use_engine=None, **kwargs):
    with open(fname, "r") as f:
        raw = f.read()

    return compile_string(raw, use_engine=use_engine, **kwargs)
