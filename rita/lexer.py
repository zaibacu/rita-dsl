import ply.lex as lex

from rita import macros





class RitaLexer(object):
    tokens = [
        'MACRO',
        'LBRACKET',
        'RBRACKET',
        'QUOTE',
        'ARROW',
    ]

    T_LBRACKET = r'{'
    T_RBRACKET = r'}'
    T_ARROW = r'->'
    T_QUOTE = r'"'

    t_ignore  = ' \t'
    t_ignore_COMMENT = r'\#.*'

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_MACRO(self, t):
        r'\w+'
        t.value = getattr(macros, t.value)   
        return t
    
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            t = self.lexer.token()
            if t is None:
                break
            yield t
