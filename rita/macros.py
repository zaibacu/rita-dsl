import logging
import types

from itertools import chain

logger = logging.getLogger(__name__)


def flatten(lst):
    if len(lst) > 1:
        return lst

    def explode(v):
        if callable(v):
            return v()
        else:
            return v

    new_lst = map(explode, lst)
    return chain(*new_lst)


def resolve_value(obj, config):
    context = []

    logger.debug("Resolving value: {0}".format(obj))

    if isinstance(obj, str):
        return obj

    elif isinstance(obj, tuple):
        return obj

    elif isinstance(obj, list):
        for item in obj:
            context.append(item)
        return context

    elif isinstance(obj, types.GeneratorType):
        return ("either", list(obj), None)

    return obj(config=config)


def ANY(config, op=None):
    return ("regex", r".*", op)


def PUNCT(config, op=None):
    return ("punct", None, op)


def MARK(type_, obj, config, op=None):
    return {
        "label": resolve_value(type_, config=config),
        "data": resolve_value(obj, config=config)
    }


def LOAD(*args, config):
    fpath = resolve_value(args[0], config=config)
    with open(fpath, "r") as f:
        return list([l.strip() for l in f.readlines()])


def ASSIGN(k, v, config, op=None):
    logger.debug("Assigning: {0} -> {1}".format(k, v))
    config.set_variable(k, resolve_value(v, config=config))


def IN_LIST(*args, config, op=None):
    variants = []
    for arg in flatten(args):
        variants.append(resolve_value(arg, config=config))
    return ("any_of", variants, None)


def PATTERN(*args, config, op=None):
    context = []
    for arg in args:
        result = resolve_value(arg, config=config)
        if isinstance(result, list):
            context += result
        else:
            context.append(result)

    return context


def WORD(*args, config, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], config=config)
        return ("value", literal, op)
    elif len(args) == 0:
        return ("regex", "(\\w|['_-])+", op)


def NUM(*args, config, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], config=config)
        return ("value", literal, op)
    elif len(args) == 0:
        return ("regex", "\\d+", op)


def POS(name, config, op=None):
    return ("pos", resolve_value(name, config=config), op)


def LEMMA(name, config, op=None):
    return ("lemma", resolve_value(name, config=config), op)


def ENTITY(name, config, op=None):
    return ("entity", resolve_value(name, config=config), op)


def PREFIX(name, config, op=None):
    return ("prefix", resolve_value(name, config=config), op)


def IMPORT(module, config):
    mod_name = resolve_value(module, config=config)
    config.register_module(mod_name)


def CONFIG(setting, value, config):
    logger.debug("Config {0} -> {1}".format(setting, value))
    config.set_config(setting, resolve_value(value, config=config))


def EXEC(obj, config):
    return resolve_value(obj, config=config)
