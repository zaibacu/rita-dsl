import logging

from rita.macros import resolve_value
from rita.utils import flatten, ExtendedOp

logger = logging.getLogger(__name__)


STOP_NAMES = {"von", "van", "de", "dos"}


def trim_name(name):
    if name in STOP_NAMES:
        return name
    return name[0] + r"\."


def trim_seniority(name):
    if name.lower() == "junior":
        return r"jr\."
    elif name.lower() == "senior":
        return r"sr\."
    else:
        return name


def remove_empty(x):
    return x.strip() != ""


def generate_names(initial_list):
    """"
    Generates variations of names
    Eg. {First Middle Last; First M. Last; F. M. Last}
    """
    for name in initial_list:
        yield name.strip(),

        buff = name.strip().split(" ")
        if len(buff) == 2:
            yield trim_name(buff[0]), buff[1]
        elif len(buff) == 3:
            if buff[2].lower() == "junior" or buff[2].lower() == "senior":
                yield buff[0], buff[1], trim_seniority(buff[2])
            else:
                yield buff[0], trim_name(buff[1]), buff[2]
                yield trim_name(buff[0]), trim_name(buff[1]), buff[2]


def NAMES(*args, config, op=None):
    if type(args[0]) == list:
        initial_list = [resolve_value(arg, config=config)
                        for arg in flatten(args)]
    else:
        initial_list = [args[0]]

    names = list([" ".join(filter(remove_empty, names))
                  for names in generate_names(initial_list)])
    print(names)
    logger.debug("Generated list of names: {}".format(names))
    new_op = ExtendedOp(op)
    new_op.case_sensitive_override = True
    return "any_of", names, new_op
