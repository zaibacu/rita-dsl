import re
import string

from rita.macros import resolve_value


char_translation = dict(
    [(c * 2, "{0}{{1,2}}".format(c)) for c in string.ascii_lowercase]
)

find_re = "|".join(["({0})".format(s) for (s, _) in char_translation.items()])

slang = {"you": "u", "for": "4", "are": "r", "you are": "ur", "you're": "ur"}


def premutations(initial):
    # return initial value
    yield initial

    """
    if we have double letters, like `oo`, we can guess that
    - user can sometimes enter both
    - sometimes only single
    """
    double_letters = re.sub(
        find_re,
        lambda x: char_translation[x.group(0)],
        initial
    )
    yield double_letters

    # if we have simple word, can add slang alternative
    if initial in slang:
        yield r"\s{0}\s".format(slang[initial])


def FUZZY(name, config, op=None):
    initial = resolve_value(name, config=config)
    return ("fuzzy", list(premutations(initial.lower())), op)
