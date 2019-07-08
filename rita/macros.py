def resolve_value(obj, context):
    if isinstance(obj, str):
        return obj.strip('"')
    return obj(context=context)

def ANY(context, op=None):
    context.append(('regex', r'.*', op))
    return context


def MARK(type_, obj, op=None):
    return {
        'label': resolve_value(type_, {}),
        'data': resolve_value(obj, {})
    }


def IN_LIST(*args, context, op=None):
    variants = []
    new_context = []
    for arg in args:
        variants.append(resolve_value(arg, new_context))
    context.append(('any_of', variants, None))
    return context


def PATTERN(*args, context=None, op=None):
    new_ctx = []
    for arg in args:
        resolve_value(arg, new_ctx)
    return new_ctx

def WORD(*args, context, op=None):
    if len(args) == 1:
        literal = args[0]
        context.append(('value', literal, op))
        return context
    elif len(args) == 0:
        return context.append(('regex', '\\w+', op))

def NUM(*args, context, op=None):
    if len(args) == 1:
        literal = args[0]
        context.append(('value', literal, op))
        return context
    elif len(args) == 0:
        return context.append(('regex', '\\d+', op))
