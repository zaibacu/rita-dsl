from rita.parser import RitaParser


def test_parser_any_macro_wo_args_wo_type():
    p = RitaParser()
    p.build()

    assert p.test('ANY') != None


def test_parser_any_macro_wo_args_w_type():
    p = RitaParser()
    p.build()

    result = p.test('ANY -> PlaceHolder')

    assert result != None


def test_parser_any_macro_w_args_wo_type():
    p = RitaParser()
    p.build()

    result = p.test('ANY{"arg1", "arg2", "arg3"}')

    assert result != None

def test_parser_any_macro_w_args_w_type():
    p = RitaParser()
    p.build()

    result = p.test('ANY{"arg1"} -> PlaceHolder')

    assert result != None
