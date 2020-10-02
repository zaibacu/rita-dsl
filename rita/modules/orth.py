from rita.macros import resolve_value


def ORTH(value, config, op=None):
    """
    Ignores case-insensitive configuration and checks words as written
    that means case-sensitive even if configuration is case-insensitive
    """
    return "orth", value, op