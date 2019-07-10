from rita.macros import resolve_value


def FUZZY(name, context, op=None):
    return context.append(("fuzzy", resolve_value(name, {}), op))
