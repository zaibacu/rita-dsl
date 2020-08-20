import inflect
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
    For a noun or a list of nouns, it will match any singluar or plural word
    Will work even if the lemmatizer is making an error
    """
    if type(args[0]) == list:
        initial_list = [resolve_value(arg, config=config)
                        for arg in flatten(args)]
    else:
        initial_list = [args[0]]
    print(initial_list)
    return "any_of", pluralizing(initial_list), op
