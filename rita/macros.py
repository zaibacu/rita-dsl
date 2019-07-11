import logging

from itertools import chain
from importlib import import_module

logger = logging.getLogger(__name__)

VARIABLES = {}
MODULES = []


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


def resolve_value(obj, context):
    logger.debug("Resolving value: {0}, context: {1}".format(obj, context))
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, list):
        for item in obj:
            context.append(item)
        return context
    return obj(context=context)


def ANY(context, op=None):
    context.append(("regex", r".*", op))
    return context


def PUNCT(context, op=None):
    context.append(("punct", None, op))
    return context


def MARK(type_, obj, op=None):
    return {"label": resolve_value(type_, []), "data": resolve_value(obj, [])}


def LOAD(*args, context=None):
    fpath = resolve_value(args[0], {})
    with open(fpath, "r") as f:
        return list([l.strip() for l in f.readlines()])


def ASSIGN(k, v, context=None, op=None):
    logger.debug("Assigning: {0} -> {1}".format(k, v))
    VARIABLES[k] = resolve_value(v, [])


def IN_LIST(*args, context, op=None):
    variants = []
    new_context = []
    for arg in flatten(args):
        variants.append(resolve_value(arg, new_context))
    context.append(("any_of", variants, None))
    return context


def PATTERN(*args, context=None, op=None):
    new_ctx = []
    for arg in args:
        resolve_value(arg, new_ctx)
    return new_ctx


def WORD(*args, context, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], [])
        context.append(("value", literal, op))
        return context
    elif len(args) == 0:
        return context.append(("regex", "\\w+", op))


def NUM(*args, context, op=None):
    if len(args) == 1:
        literal = resolve_value(args[0], {})
        context.append(("value", literal, op))
        return context
    elif len(args) == 0:
        return context.append(("regex", "\\d+", op))


def POS(name, context, op=None):
    return context.append(("pos", resolve_value(name, {}), op))


def LEMMA(name, context, op=None):
    return context.append(("lemma", resolve_value(name, {}), op))


def ENTITY(name, context, op=None):
    return context.append(("entity", resolve_value(name, {}), op))


def IMPORT(module, context=None, op=None):
    mod_name = resolve_value(module, {})
    MODULES.append(import_module(mod_name))

    
def EXEC(obj, context=None, op=None):
    return resolve_value(obj, [])
