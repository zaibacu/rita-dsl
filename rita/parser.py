import logging

import ply.yacc as yacc

from functools import partial

from rita.lexer import RitaLexer
from rita import macros

logger = logging.getLogger(__name__)


def stub(*args, **kwargs):
    return None


def either(a, b):
    yield a
    yield b


def load_macro(name, config):
    try:
        return partial(getattr(macros, name), config=config)
    except Exception:
        pass

    def lazy_load(*args, **kwargs):
        print(config.modules)
        for mod in config.modules:
            try:
                fn = getattr(mod, name)
                return fn(*args, **kwargs)
            except Exception as ex:
                logger.error(ex)
                continue

        raise RuntimeError("MACRO {} not loaded".format(name))

    return lazy_load


def var_wrapper(variable, config):
    def wrapper(*args, **kwargs):
        logger.debug("Variables: {}".format(config.variables))
        return config.get_variable(variable)

    return wrapper


class RitaParser(object):
    tokens = RitaLexer.tokens
    precedence = (
        ("nonassoc", "ARROW"),
        ("nonassoc", "PIPE"),
        ("nonassoc", "COMMA"),
        ("left", "EXEC"),
        ("left", "ASSIGN"),
        ("left", "RBRACKET", "LBRACKET", "LPAREN", "RPAREN"),
        ("left", "KEYWORD", "NAME", "LITERAL"),
        ("right", "MODIF_QMARK", "MODIF_STAR", "MODIF_PLUS"),
    )

    def __init__(self, config):
        self.config = config
        self.lexer = None
        self.parser = None

    def p_document(self, p):
        """
        DOCUMENT : MACRO_CHAIN
                 | MACRO_EXEC
                 | VARIABLE
        """
        logger.debug("Building initial document {}".format(p[1]))
        p[0] = [p[1]]

    def p_document_list(self, p):
        """
        DOCUMENT : DOCUMENT MACRO_CHAIN
                 | DOCUMENT MACRO_EXEC
                 | DOCUMENT VARIABLE
        """
        logger.debug("Extending document {}".format(p[2]))
        p[0] = p[1] + [p[2]]

    def p_macro_chain(self, p):
        " MACRO_CHAIN : MACRO ARROW MACRO "
        logger.debug("Have {0} -> {1}".format(p[1], p[3]))
        p[0] = partial(
            p[3],
            macros.PATTERN(p[1], config=self.config),
            config=self.config
        )

    def p_macro_chain_from_array(self, p):
        " MACRO_CHAIN : ARRAY ARROW MACRO "
        logger.debug("Have {0} -> {1}".format(p[1], p[3]))
        p[0] = partial(
            p[3],
            macros.PATTERN(*p[1], config=self.config),
            config=self.config
        )

    def p_macro_exec(self, p):
        " MACRO_EXEC : EXEC MACRO "
        logger.debug("Exec {0}".format(p[2]))
        macros.EXEC(p[2], config=self.config)
        p[0] = stub

    def p_macro_w_modif(self, p):
        """
        MACRO : MACRO MODIF_PLUS
              | MACRO MODIF_STAR
              | MACRO MODIF_QMARK
              | MACRO EXEC
        """
        logger.debug("Adding modifier to Macro {}".format(p[1]))
        fn = p[1]
        p[0] = partial(fn, op=p[2])

    def p_macro_wo_args(self, p):
        " MACRO : KEYWORD "
        fn = load_macro(p[1], config=self.config)
        logger.debug("Parsing macro (w/o args): {}".format(p[1]))
        p[0] = fn

    def p_macro_w_args(self, p):
        " MACRO : KEYWORD LPAREN ARGS RPAREN "
        logger.debug("Parsing macro: {0}, args: {1}".format(p[1], p[3]))
        fn = load_macro(p[1], config=self.config)
        p[0] = partial(fn, *p[3])

    def p_macro_from_array(self, p):
        " MACRO : KEYWORD ARRAY "
        logger.debug("Parsing macro: {0}, args: {1}".format(p[1], p[2]))
        fn = load_macro(p[1], config=self.config)
        p[0] = partial(fn, *p[2])

    def p_array(self, p):
        " ARRAY : LBRACKET ARGS RBRACKET "
        p[0] = p[2]

    def p_variable(self, p):
        " VARIABLE_NAME : NAME "
        p[0] = var_wrapper(p[1], self.config)

    def p_variable_from_args(self, p):
        " VARIABLE : NAME ASSIGN ARGS "
        if len(p[3]) == 1:
            macros.ASSIGN(p[1], p[3][0], config=self.config)
        else:
            macros.ASSIGN(p[1], p[3], config=self.config)

        p[0] = stub

    def p_either(self, p):
        " ARG : ARG PIPE ARG "
        p[0] = either(p[1], p[3])

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
        " ARG : VARIABLE_NAME "
        p[0] = p[1]()

    def p_arg_from_array(self, p):
        " ARGS : ARRAY "
        p[0] = p[1]

    def p_error(self, p):
        if p:
            logger.error("Syntax error at '{}'".format(p.value))
        else:
            logger.error("p is null")

    def build(self, **kwargs):
        self.lexer = RitaLexer().build(**kwargs)
        self.parser = yacc.yacc(module=self, errorlog=logger, **kwargs)

    def parse(self, data):
        if data.strip() == "":
            return []

        return self.parser.parse(r"{}".format(data), lexer=self.lexer, debug=logger)
