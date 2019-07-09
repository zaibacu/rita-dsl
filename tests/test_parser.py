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

def test_parser_assign_literal_and_ignore_it():
    p = RitaParser()
    p.build()

    results = p.test('''
    my_variable = "Test"

    PATTERN{WORD{"something"}} -> MARK{"TEST"}
    ''')
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "something", None)]} == rules


def test_parser_assign_literal_and_use_it():
    p = RitaParser()
    p.build()

    results = p.test('''
    my_variable = "Test"

    PATTERN{WORD{my_variable} -> MARK{"TEST"}
    ''')
    assert len(results) == 1

    rules = results[0]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "TEST", None)]} == rules

def test_parser_just_assign_macro():
    p = RitaParser()
    p.build()

    results = p.test('''
    x = WORD{"Test"}
    ''')
    assert len(results) == 1

    rules = results[0]()

    print(rules)
    assert {"vars": {"x": [("value", "Test", None)]}} == rules

def test_parser_assign_macro_and_use_it():
    p = RitaParser()
    p.build()

    results = p.test('''
    my_variable = WORD{"Test"}

    PATTERN{my_variable -> MARK{"TEST"}
    ''')
    assert len(results) == 1

    rules = results[0]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "TEST", None)]} == rules

