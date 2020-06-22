import logging
import ply.lex as lex

logger = logging.getLogger(__name__)


class RitaLexer(object):
    tokens = [
        "KEYWORD",
        "LITERAL",
        "NAME",
        "LBRACKET",
        "RBRACKET",
        "LPAREN",
        "RPAREN",
        "ARROW",
        "COMMA",
        "MODIF_QMARK",
        "MODIF_STAR",
        "MODIF_PLUS",
        "ASSIGN",
        "EXEC",
        "PIPE",
    ]

    literals = ["{", "}", "(", ")", '"', ",", "=", "!", "|"]

    t_ignore = " \t"
    t_ignore_COMMENT = r"\#.*"
    t_ARROW = "->"
    t_LBRACKET = "{"
    t_RBRACKET = "}"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_COMMA = ","
    t_MODIF_QMARK = r"\?"
    t_MODIF_STAR = r"\*"
    t_MODIF_PLUS = r"\+"
    t_EXEC = r"!"
    t_ASSIGN = r"="
    t_PIPE = r"\|"

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_KEYWORD(self, t):
        r"[A-Z_]{3,}"
        return t

    def t_LITERAL(self, t):
        r'("|\')(\\.|.)+?("|\')'
        t.value = t.value[1:-1]
        return t

    def t_NAME(self, t):
        r"\w+"
        return t

    def t_error(self, t):
        logger.error("Invalid Token: {}".format(t.value[0]))
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, errorlog=logger, **kwargs)
        return self.lexer

    def tokenize(self, data):
        self.lexer.input(data)
        while True:
            t = self.lexer.token()
            if t is None:
                break
            yield t
