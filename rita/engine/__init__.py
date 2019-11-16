def get_default():
    try:
        import spacy
        from .translate_spacy import compile_tree
        return compile_tree
    except ImportError:
        from .translate_standalone import compile_tree
        return compile_tree
