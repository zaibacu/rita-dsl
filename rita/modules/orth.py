from rita.utils import ExtendedOp


def ORTH(value, config, op=None):
    """
    Ignores case-insensitive configuration and checks words as written
    that means case-sensitive even if configuration is case-insensitive
    """
    new_op = ExtendedOp(op)
    new_op.case_sensitive_override = True
    return "orth", value, new_op
