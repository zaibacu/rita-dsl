import logging
import ply.yacc as yacc

from functools import partial

from rita.lexer import RitaLexer
from rita import macros

logger = logging.getLogger(__name__)


def stub(*args, **kwargs):
    return None

def var_wrapper(variable):
    def wrapper(*args, **kwargs):
        print(VARIABLES)
        return VARIABLES[variable]

    return wrapper

VARIABLES = {}


def get_macro(name):
    if name in VARIABLES:
        return var_wrapper(VARIABLES[name])

    try:
        return getattr(macros, name)
    except:
        logger.error("{0} macro not found".format(name))
        return stub


class RitaParser(object):
    tokens = RitaLexer.tokens
    precedence = (
        ("nonassoc", "ARROW"),
        ("nonassoc", "COMMA"),
        ("nonassoc", "ASSIGN"),
        ("left", "RBRACKET", "LBRACKET"),
        ("left", "KEYWORD", "LITERAL"),
        ("right", "MODIF_QMARK", "MODIF_STAR", "MODIF_PLUS"),
    )


    def p_document(self, p):
        " DOCUMENT : MACRO_CHAIN "
        logger.debug("Building initial document {}".format(p[1]))
        p[0] = [p[1]]

    def p_document_list(self, p):
        " DOCUMENT : DOCUMENT MACRO_CHAIN "
        logger.debug("Extending document {}".format(p[2]))
        p[0] = p[1] + [p[2]]

    def p_macro_chain(self, p):
        " MACRO_CHAIN : MACRO ARROW MACRO "
        logger.debug("Have {0} -> {1}".format(p[1], p[3]))
        p[0] = partial(p[3], p[1])

    def p_variable(self, p):
        " VARIABLE : KEYWORD ASSIGN ARG "
        logger.debug("Parsing variable: {0} = {1}".format(p[1], p[3]))
        VARIABLES[p[1]] = p[3]
        p[0] = p[3]

    def p_macro_w_modif(self, p):
        " MACRO : MACRO MODIF_PLUS "
        logger.debug("Adding modifier to Macro {}".format(p[1]))
        fn = p[1]
        p[0] = partial(fn, op=p[2])

    def p_macro_wo_args(self, p):
        " MACRO : KEYWORD "
        try:
            fn = getattr(macros, p[1])
            logger.debug("Parsing macro (w/o args): {}".format(p[1]))
            p[0] = fn
        except:
            p[0] = var_wrapper(p[1])

    def p_macro_w_args(self, p):
        " MACRO : KEYWORD LBRACKET ARGS RBRACKET "
        try:
            fn = getattr(macros, p[1])
            logger.debug("Parsing macro: {0}, args: {1}".format(p[1], p[3]))
            p[0] = partial(fn, *p[3])
        except:
            p[0] = stub

    def p_arg_list(self, p):
        " ARGS : ARGS COMMA ARG "
        p[0] = p[1] + [p[3]]

    def p_args(self, p):
        " ARGS : ARG "
        p[0] = [p[1]]

    def p_arg(self, p):
        " ARG : LITERAL "
        p[0] = p[1]

    def p_arg_from_macro(self, p):
        " ARG : MACRO "
        p[0] = p[1]

    def p_arg_from_var(self, p):
        " ARG : VARIABLE "
        p[0] = p[1]

    def p_error(self, p):
        logger.error("Syntax error at '{}'".format(p.value))

    def build(self, **kwargs):
        self.lexer = RitaLexer().build(**kwargs)
        self.parser = yacc.yacc(module=self, **kwargs)

    def test(self, data):
        return self.parser.parse(data, lexer=self.lexer)
