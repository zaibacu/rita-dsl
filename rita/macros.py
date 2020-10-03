import logging
import types

from rita.utils import flatten, ExtendedOp

logger = logging.getLogger(__name__)


def resolve_value(obj, config):
    logger.debug("Resolving value: {0}".format(obj))

    if isinstance(obj, str):
        return obj

    elif isinstance(obj, tuple):
        return obj

    elif isinstance(obj, list):
        return obj

    elif isinstance(obj, types.GeneratorType):
        return "either", list(obj), ExtendedOp(None)

    return obj(config=config)


def ANY(config, op=None):
    return "regex", r".*", ExtendedOp(op)


def PUNCT(config, op=None):
    return "punct", None, ExtendedOp(op)


def MARK(type_, obj, config, op=None):
    return {
        "label": resolve_value(type_, config=config),
        "data": resolve_value(obj, config=config)
    }


def LOAD(*args, config):
    fpath = resolve_value(args[0], config=config)
    with open(fpath, "r") as f:
        return list([line.strip() for line in f.readlines()])


def ASSIGN(k, v, config, op=None):
    logger.debug("Assigning: {0} -> {1}".format(k, v))
    config.set_variable(k, resolve_value(v, config=config))


def IN_LIST(*args, config, op=None):
    return "any_of", [resolve_value(arg, config=config)
                      for arg in flatten(args)], ExtendedOp(op)


def PATTERN(*args, config, op=None):
    context = []
    for arg in args:
        result = resolve_value(arg, config=config)
        if isinstance(result, list):
            context.append(NESTED(result, config, op))
        else:
            context.append(result)

    return context


def NESTED(children, config, op=None):
    return "nested", children, op


def WORD(*args, config, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], config=config)
        return "value", literal, ExtendedOp(op)
    elif len(args) == 0:
        return "regex", r"((\w|['_-])+)", ExtendedOp(op)


def NUM(*args, config, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], config=config)
        return "value", literal, ExtendedOp(op)
    elif len(args) == 0:
        return "regex", r"((\d+[\.,]\d+)|(\d+))", ExtendedOp(op)


def POS(name, config, op=None):
    return "pos", resolve_value(name, config=config), ExtendedOp(op)


def LEMMA(name, config, op=None):
    return "lemma", resolve_value(name, config=config), ExtendedOp(op)


def ENTITY(name, config, op=None):
    return "entity", resolve_value(name, config=config), ExtendedOp(op)


def PREFIX(name, config, op=None):
    return "prefix", resolve_value(name, config=config), ExtendedOp(op)


def IMPORT(module, config):
    mod_name = resolve_value(module, config=config)
    config.register_module(mod_name)


def CONFIG(setting, value, config):
    logger.debug("Config {0} -> {1}".format(setting, value))
    config.set_config(setting, resolve_value(value, config=config))


def EXEC(obj, config):
    return resolve_value(obj, config=config)
