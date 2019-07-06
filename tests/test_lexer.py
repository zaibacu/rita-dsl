from pytest import fixture
from rita.lexer import RitaLexer



def test_tokenize_any_macro_wo_args():
    l = RitaLexer()
    l.build()

    tokens = list(l.test('ANY'))
    assert len(tokens) == 1
