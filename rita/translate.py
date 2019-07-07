'''
[{'data': [{'any_of': ['red', 'green', 'blue', 'white', 'black']}, {'value': 'car'}], 'label': 'COLORED_CAR'}, {'data': [{'any_of': ['BMW', 'Audi', 'VW', 'Toyota', 'Mazda']}, {'regex': '.*'}], 'label': 'CAR_MODEL'}]

'''


ACTIONS = {
    'any_of': lambda x: {'TEXT': {'REGEX': '({})'.format('|'.join(x))}},
    'value': lambda x: {'LOWER': x},
    'regex': lambda x: {'TEXT': {'REGEX': x}},
}


def context_to_patterns(context):
    patterns = []

    def build_pattern(c):
        data = c['data']
        pattern = {}
        pattern['label'] = c['label']
        pattern['pattern'] = [ACTIONS[t](d) for t, d in c['data']]
        return pattern

    for c in context:
        patterns.append(build_pattern(c))

    return patterns
