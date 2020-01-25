import rita


def setup_spacy(model, patterns=None, rules_path=None, rules_string=None, override_ents=True):
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
