from rita.macros import resolve_value


def FUZZY(name, context, op=None):
    context.append(("fuzzy", resolve_value(name, {}), op))
    return context
