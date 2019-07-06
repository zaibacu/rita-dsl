import ply.yacc as yacc

from functools import partial

from rita.lexer import RitaLexer
from rita import macros

def stub(*args, **kwargs):
    return None

def get_macro(name):
    try:
        return getattr(macros, name)
    except:
        print('{0} macro not found'.format(name))
        return stub
    

class RitaParser(object):
    tokens = RitaLexer.tokens
    precedence = (
        ('nonassoc', 'ARROW'),
        ('nonassoc', 'COMMA'),
        ('left', 'QUOTE'),
        ('left', 'RBRACKET', 'LBRACKET'),
        ('left', 'KEYWORD')
    )

    def p_macro_chain(self, p):
        ' MACRO : MACRO ARROW MACRO '
        print('Have {0} -> {1}'.format(p[1], p[3]))
        p[0] = partial(p[3], p[1])

    def p_macro_wo_args(self, p):
        ' MACRO : KEYWORD '
        print('Parsing macro (w/o args): {}'.format(p[1]))
        fn = get_macro(p[1])
        p[0] = fn

    def p_macro_w_args(self, p):
        ' MACRO : KEYWORD LBRACKET ARGS RBRACKET '
        print('Parsing macro: {0}, args: {1}'.format(p[1], p[3]))
        fn = get_macro(p[1])
        p[0] = partial(fn, *p[3])

    def p_arg_list(self, p):
        ' ARGS : ARGS COMMA ARG '
        p[0] = p[1] + [p[3]]

    def p_args(self, p):
        ' ARGS : ARG '
        p[0] = [p[1]]

    def p_arg(self, p):
        ' ARG : QUOTE KEYWORD QUOTE '
        p[0] = p[2]

    def p_arg_from_macro(self, p):
        ' ARG : MACRO '
        p[0] = p[1]

    def p_error(self, p):
        print("Syntax error at '{}'".format(p.value))

    def build(self, **kwargs):
        self.lexer = RitaLexer().build(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data):
        return self.parser.parse(data, lexer=self.lexer)
