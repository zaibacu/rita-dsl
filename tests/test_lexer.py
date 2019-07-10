from pytest import fixture
from rita.lexer import RitaLexer
from rita import macros


def test_tokenize_any_macro_wo_args_wo_type():
    l = RitaLexer()
    l.build()

    tokens = list(l.tokenize("ANY"))
    assert len(tokens) == 1
    t = tokens[0]
    assert t.type == "KEYWORD"
    assert t.value == "ANY"


def test_tokenize_any_macro_wo_args_w_type():
    l = RitaLexer()
    l.build()

    tokens = list(l.tokenize('ANY -> MARK{"Placeholder"}'))
    assert len(tokens) == 6
    t0 = tokens[0]
    assert t0.type == "KEYWORD"
    assert t0.value == "ANY"

    assert tokens[1].type == "ARROW"

    t2 = tokens[2]

    assert t2.type == "KEYWORD"
    assert t2.value == "MARK"

    t3 = tokens[4]

    assert t3.type == "LITERAL"
    assert t3.value == "Placeholder"


def test_tokenize_assign_literal():
    l = RitaLexer()
    l.build()

    tokens = list(l.tokenize('Test = "Test"'))

    assert len(tokens) == 3

    assert tokens[0].type == "NAME"
    assert tokens[1].type == "ASSIGN"
    assert tokens[2].type == "LITERAL"


def test_tokenize_assign_macro():
    l = RitaLexer()
    l.build()

    tokens = list(l.tokenize('Test = WORD{"Test"}'))

    assert len(tokens) == 6

    assert tokens[0].type == "NAME"
    assert tokens[1].type == "ASSIGN"
    assert tokens[2].type == "KEYWORD"
    assert tokens[4].type == "LITERAL"
