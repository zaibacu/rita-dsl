try:
    import spacy
    from .translate_spacy import compile_rules
except ImportError:
    from .translate_standalone import compile_rules


def get_default():
    return compile_rules
