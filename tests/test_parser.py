from rita.parser import RitaParser


def test_parser_any_macro_wo_args_w_type():
    p = RitaParser()
    p.build()

    results = p.test('ANY -> MARK{"PlaceHolder"}')
    assert len(results) == 1


def test_parser_any_macro_w_args_w_type():
    p = RitaParser()
    p.build()

    results = p.test('PATTERN{WORD{"arg1"}} -> MARK{"PlaceHolder"}')
    assert len(results) == 1


def test_parser_nested_macro():
    p = RitaParser()
    p.build()

    results = p.test('PATTERN{ANY, WORD{"test"}} -> MARK{"Test"}')
    assert len(results) == 1
    for result in results:
        print(result())

def test_parser_assign_literal():
    p = RitaParser()
    p.build()

    results = p.test('''
    TEST = "Test"

    PATTERN{WORD{TEST}} -> MARK{"TEST"}
    ''')
    assert len(results) == 1

    rules = results[0]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "Test", None)]} == rules

