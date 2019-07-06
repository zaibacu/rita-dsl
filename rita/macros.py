def ANY(*args):
    return {'TEXT': {'REGEX': '.*'}}


def MARK(obj, type_, *args):
    return {'label': type_, 'pattern': [obj]}


def IN_LIST(*args):
    pass


def PATTERN(*args):
    pass


def WORD(literal):
    pass
