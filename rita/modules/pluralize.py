import sys
import logging
try:
    import inflect
except ImportError:
    logging.exception(
        "Pluralize module requires 'inflect' package to be installed."
        "Install it and try again"
    )
    sys.exit(1)

from rita.macros import resolve_value
from rita.utils import flatten


def pluralizing(initial_list):
    """"
    For a list of nouns, it will return a list of the plurals and the initial nouns
    """
    p = inflect.engine()
    plurals = [p.plural(word) for word in initial_list]
    return initial_list + plurals


def PLURALIZE(*args, config, op=None):
    """
    For a noun or a list of nouns, it will match any singular or plural word
    Usage for a single word, e.g.:
    PLURALIZE("car")
    Usage for lists, e.g.:
    vehicles = {"car", "bicycle", "ship"}
    PLURALIZE(vehicles)
    Will work even for regex or if the lemmatizer of spaCy is making an error
    Has dependency to the Python inflect package https://pypi.org/project/inflect/
    """
    if type(args[0]) == list:
        initial_list = [resolve_value(arg, config=config)
                        for arg in flatten(args)]
    else:
        initial_list = [args[0]]
    return "any_of", pluralizing(initial_list), op
