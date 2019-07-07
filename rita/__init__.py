from rita.parser import RitaParser

def compile(fname):
    parser = RitaParser()
    parser.build()
    with open(fname, 'r') as f:
        raw = f.read()

    root = parser.test(raw)
    result = []
    for doc in root:
        result.append(doc())
    return result

    
