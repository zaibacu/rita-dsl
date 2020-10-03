from rita.utils import ExtendedOp


def REGEX(regex_pattern, config, op=None):
    """
    Matches words based on a Regex pattern
    e.g. all words that start with an 'a' would be
    REGEX("^a")
    """
    new_op = ExtendedOp(op)
    new_op.local_regex_override = True
    return "regex", regex_pattern, new_op
