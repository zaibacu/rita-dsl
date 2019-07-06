from rita.parser import RitaParser

def compile(fname):
    parser = RitaParser()
    parser.build()
    with open(fname, 'r') as f:
        raw = f.read()

    root = parser.test(raw)
    return root()

    
