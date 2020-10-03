from rita.utils import ExtendedOp


def TAG(tag, config, op=None):
    """
    For generating POS/TAG patterns based on a Regex
    e.g. TAG("^NN|^JJ") for nouns or adjectives
    """
    values = {"tag": tag}
    return "tag", values, ExtendedOp(op)


def TAG_WORD(tag, value, config, op=None):
    """
    For generating TAG patterns with a word or a list
    e.g. match only "proposed" when it is in the sentence a verb (and not an adjective):
    TAG_WORD("^VB", "proposed")
    e.g. match a list of words only to verbs
    words = {"percived", "proposed"}
    {TAG_WORD("^VB", words)?}->MARK("LABEL")
    """
    values = {"tag": tag}
    if type(value) == list:
        values["list"] = value
    else:
        values["word"] = value
    return "tag", values, ExtendedOp(op)
