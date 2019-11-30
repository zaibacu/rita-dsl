class Config(object):
    @property
    def list_ignore_case(self):
        """
        Ignore case while doing `IN_LIST` operation
        """
        return True

    @property
    def implicit_punct(self):
        """
        Automatically add optional Punctuation characters inside rule between macros.
        eg. `WORD(w1), WORD(w2)`
        would be converted into:
        `WORD(w1), PUNCT?, WORD(w2)`
        """
        return True
