def resolve_value(obj, context):
    if isinstance(obj, str):
        return obj
    return obj(context=context)

def ANY(context):
    context.append({'regex': r'.*'})
    return context


def MARK(type_, obj, context=None):
    if context is None:
        context = []

    context.append({
        'label': type_,
        'data': resolve_value(obj, context)
    })

    return context


def IN_LIST(*args, context):
    variants = []
    new_context = []
    for arg in args:
        variants.append(resolve_value(arg, new_context))
    context.append({'any_of':  variants})
    return context


def PATTERN(*args, context=None):
    new_ctx = []
    for arg in args:
        resolve_value(arg, new_ctx)
    return new_ctx


def WORD(literal, context):
    context.append({'value': literal})
    return context
