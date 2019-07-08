def any_of_parse(lst, op=None):
    if op:
        return {'TEXT': {'REGEX': r'({0})'.format('|'.join(lst))}, 'OP': op}
    else:
        return {'TEXT': {'REGEX': r'({})'.format('|'.join(lst))}}

def value_parse(v, op=None):
    if op:
        return {'ORTH': v, 'OP': op}
    else:
        return {'ORTH': v}

def regex_parse(r, op=None):
    if op:
        return {'TEXT': {'REGEX': r}, 'OP': op}
    else:
        return {'TEXT': {'REGEX': r}}


PARSERS = {
    'any_of': any_of_parse,
    'value': value_parse,
    'regex': regex_parse,
    
}

def rules_to_patterns(rule):
    return {
        'label': rule['label'],
        'pattern': [PARSERS[t](d, op) for (t, d, op) in rule['data']]
    }
