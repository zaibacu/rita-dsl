from pytest import fixture
from rita.lexer import RitaLexer
from rita import macros



def test_tokenize_any_macro_wo_args():
    l = RitaLexer()
    l.build()

    tokens = list(l.test('ANY'))
    assert len(tokens) == 1
    t = tokens[0]
    assert t.type == 'MACRO'
    assert t.value == macros.ANY
