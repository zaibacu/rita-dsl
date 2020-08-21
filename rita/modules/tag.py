from rita.macros import resolve_value


def TAG(name, config, op=None):
    """
    For generating POS/TAG patterns based on a Regex
    e.g. TAG("^NN|^JJ") for nouns or adjectives
    """
    return "tag", resolve_value(name, config=config), op
