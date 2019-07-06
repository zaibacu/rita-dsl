def ANY(*args, **kwargs):
    return {'TEXT': {'REGEX': '.*'}}

def SET_TYPE(obj, type_, *args, **kwargs):
    return {'label': type_, 'pattern': [obj]}
