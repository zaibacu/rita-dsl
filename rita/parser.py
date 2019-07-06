import ply.yacc as yacc

from rita.lexer import RitaLexer
from rita import macros

class RitaParser(object):
    tokens = RitaLexer.tokens

    def p_macro_type(self, p):
        ' MACRO : MACRO ARROW KEYWORD '
        p[0] = macros.SET_TYPE(p[1], p[3])

    def p_macro_wo_args(self, p):
        ' MACRO : KEYWORD '
        try:
            fn = getattr(macros, p[1])
            p[0] = fn()
        except:
            print('{0} macro not found'.format(p[1]))
            p[0] = None

    def p_macro_w_args(self, p):
        ' MACRO : KEYWORD LBRACKET ARGS RBRACKET '
        try:
            fn = getattr(macros, p[1])
            p[0] = fn(*p[3])
        except:
            print('{0} macro not found'.format(p[1]))
            p[0] = None

    def p_arg_list(self, p):
        ' ARGS : ARGS COMMA ARG '
        p[0] = p[1] + [p[3]]

    def p_args(self, p):
        ' ARGS : ARG '
        p[0] = [p[1]]

    def p_arg(self, p):
        ' ARG : QUOTE KEYWORD QUOTE '
        p[0] = p[2]

    def p_error(self, p):
        print("Syntax error at '{}'".format(p.value))

    def build(self, **kwargs):
        self.lexer = RitaLexer().build(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data):
        return self.parser.parse(data, lexer=self.lexer)
