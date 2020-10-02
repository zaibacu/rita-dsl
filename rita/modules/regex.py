def REGEX(regex_pattern, config, op=None):
    """
    Matches words based on a Regex pattern
    e.g. all words that start with an 'a' would be
    REGEX("^a")
    """
    return "regex", regex_pattern, op
