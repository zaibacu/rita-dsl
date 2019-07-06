import ply.lex as lex

from rita import macros



class RitaLexer(object):
    tokens = [
        'KEYWORD',
        'LBRACKET',
        'RBRACKET',
        'QUOTE',
        'ARROW',
        'COMMA',
    ]

    literals = ['{', '}', '"', ',']

    t_ignore = ' \t'
    t_ignore_COMMENT = r'\#.*'
    t_ARROW = '->'
    t_QUOTE = '"'
    t_LBRACKET = '{'
    t_RBRACKET = '}'
    t_COMMA = ','

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_KEYWORD(self, t):
        r'(\w|[_])+'
        return t
    
    def t_error(self, t):
        print('Invalid Token: {}'.format(t.value[0]))
        t.lexer.skip( 1 )

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

    def test(self, data):
        self.lexer.input(data)
        while True:
            t = self.lexer.token()
            if t is None:
                break
            yield t
