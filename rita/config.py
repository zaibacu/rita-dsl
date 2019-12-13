import operator

try:
    import spacy
    from rita.engine.translate_spacy import compile_rules as spacy_engine
except ImportError:
    pass

from rita.engine.translate_standalone import compile_rules as standalone_engine

from rita.utils import SingletonMixin


class Config(SingletonMixin):
    def __init__(self):
        self.available_engines = []
        self.engines_by_key = {}

        try:
            self.register_engine(1, "spacy", spacy_engine)
        except NameError:
            # spacy_engine is not imported
            pass
        self.register_engine(2, "standalone", standalone_engine)

    def register_engine(self, priority, key, compile_fn):
        self.available_engines.append((priority, key, compile_fn))
        self.engines_by_key[key] = compile_fn
        sorted(self.available_engines, key=operator.itemgetter(0))

    @property
    def default_engine(self):
        (_, _, compile_fn) = self.available_engines[0]
        return compile_fn

    def get_engine(self, key):
        return self.engines_by_key[key]
        


class SessionConfig(object):
    def __init__(self):
        self._list_ignore_case = True
        self._implicit_punct = True
        self._root = Config()
    
    @property
    def list_ignore_case(self):
        """
        Ignore case while doing `IN_LIST` operation
        """
        return self._list_ignore_case

    @property
    def implicit_punct(self):
        """
        Automatically add optional Punctuation characters inside rule between macros.
        eg. `WORD(w1), WORD(w2)`
        would be converted into:
        `WORD(w1), PUNCT?, WORD(w2)`
        """
        return self._implicit_punct

    @implicit_punct.setter
    def implicit_punct(self, val):
        self._implicit_punct = val

    @list_ignore_case.setter
    def list_ignore_case(self, val):
        self._list_ignore_case = val

    def __getattr__(self, name):
        if name == "_root":
            return self._root

        return getattr(self._root, name)


def with_config(fn):
    def wrapper(*args, **kwargs):
        config = SessionConfig()
        return fn(*args, config=config, **kwargs)

    return wrapper
