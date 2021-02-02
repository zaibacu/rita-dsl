import rita


def setup_spacy(model, patterns=None, rules_path=None, rules_string=None, override_ents=True):
    import spacy
    major, _, _ = spacy.__version__.split(".")
    if major == "2":
        return _spacy_v2(model, patterns, rules_path, rules_string, override_ents)
    elif major == "3":
        return _spacy_v3(model, patterns, rules_path, rules_string, override_ents)
    else:
        raise RuntimeError("Unsupported spaCy version: {}".format(major))


def _spacy_v2(model, patterns=None, rules_path=None, rules_string=None, override_ents=True):
    from spacy.pipeline import EntityRuler
    ruler = EntityRuler(model, overwrite_ents=override_ents)
    if not patterns:
        if rules_path:
            patterns = rita.compile(rules_path, use_engine="spacy")
        elif rules_string:
            patterns = rita.compile_string(rules_string, use_engine="spacy")
        else:
            raise RuntimeError("Please provides rules. Either `patterns`, `rules_path` or `rules_string`")

        ruler.add_patterns(patterns)
    else:
        ruler.from_disk(patterns)

    model.add_pipe(ruler)
    return model


def _spacy_v3(model, patterns=None, rules_path=None, rules_string=None, override_ents=True):
    ruler = model.add_pipe("entity_ruler", config={"overwrite_ents": override_ents, "validate": True})
    if not patterns:
        if rules_path:
            patterns = rita.compile(rules_path, use_engine="spacy")
        elif rules_string:
            patterns = rita.compile_string(rules_string, use_engine="spacy")
        else:
            raise RuntimeError("Please provides rules. Either `patterns`, `rules_path` or `rules_string`")

        ruler.add_patterns(patterns)
    else:
        ruler.from_disk(patterns)
    return model
