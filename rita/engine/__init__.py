try:
    import spacy
    from .translate_spacy import compile_tree
except ImportError:
    from .translate_standalone import compile_tree


def get_default():
    return compile_tree
