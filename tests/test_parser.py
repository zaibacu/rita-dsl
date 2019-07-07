from rita.parser import RitaParser


def test_parser_any_macro_wo_args_wo_type():
    p = RitaParser()
    p.build()

    assert p.test('ANY') != None


def test_parser_any_macro_wo_args_w_type():
    p = RitaParser()
    p.build()

    result = p.test('ANY -> MARK{"PlaceHolder"}')

    assert result != None


def test_parser_any_macro_w_args_w_type():
    p = RitaParser()
    p.build()

    result = p.test('PATTERN{WORD{"arg1"}} -> MARK{"PlaceHolder"}')

    assert result != None

def test_parser_nested_macro():
    p = RitaParser()
    p.build()

    result = p.test('PATTERN{ANY, WORD{"test"}} -> MARK{"Test"}')
    assert result != None

    print(result)
    print(result([]))
