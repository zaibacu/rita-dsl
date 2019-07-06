from pytest import fixture
from rita.lexer import RitaLexer
from rita import macros


def test_tokenize_any_macro_wo_args_wo_type():
    l = RitaLexer()
    l.build()

    tokens = list(l.test('ANY'))
    assert len(tokens) == 1
    t = tokens[0]
    assert t.type == 'KEYWORD'
    assert t.value == 'ANY'

def test_tokenize_any_macro_wo_args_w_type():
    l = RitaLexer()
    l.build()

    tokens = list(l.test('ANY -> PlaceHolder'))
    assert len(tokens) == 3
    t0 = tokens[0]
    assert t0.type == 'KEYWORD'
    assert t0.value == 'ANY'

    assert tokens[1].type == 'ARROW'

    t2 = tokens[2]

    assert t2.type == 'KEYWORD'
    assert t2.value == 'PlaceHolder'
