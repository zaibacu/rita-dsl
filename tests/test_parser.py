from rita.parser import RitaParser


def test_parser_any_macro_wo_args_w_type():
    p = RitaParser()
    p.build()

    results = p.parse('ANY -> MARK("PlaceHolder")')
    assert len(results) == 1


def test_parser_any_macro_w_args_w_type():
    p = RitaParser()
    p.build()

    results = p.parse('{WORD("arg1")} -> MARK("PlaceHolder")')
    assert len(results) == 1


def test_parser_nested_macro():
    p = RitaParser()
    p.build()

    results = p.parse('{ANY, WORD("test")} -> MARK("Test")')
    assert len(results) == 1
    for result in results:
        print(result())


def test_parser_assign_literal_and_ignore_it():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    my_variable = "Test"

    {WORD("something")} -> MARK("TEST")
    """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "something", None)]} == rules


def test_parser_assign_literal_and_use_it():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    my_variable = "Test"

    {WORD(my_variable)} -> MARK("TEST")
    """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "Test", None)]} == rules


def test_parser_just_assign_macro():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    x = WORD("Test")
    """
    )
    assert len(results) == 1


def test_parser_assign_macro_and_use_it():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    my_variable = WORD("Test")

    {my_variable} -> MARK("TEST")
    """
    )
    assert len(results) == 2

    rules = results[1]()

    print(rules)
    assert {"label": "TEST", "data": [("value", "Test", None)]} == rules


def test_parser_import_module():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    IMPORT("rita.modules.fuzzy") -> EXEC

    FUZZY("test") -> MARK("FUZZY_MATCH")
    """
    )

    assert len(results) == 2
    results[0]()
    rules = results[1]()
    print(rules)


def test_parser_import_module_shortcut():
    p = RitaParser()
    p.build(debug=True)

    results = p.parse(
        """
    !IMPORT("rita.modules.fuzzy")

    FUZZY("test") -> MARK("FUZZY_MATCH")
    """
    )

    assert len(results) == 2
    results[0]()
    rules = results[1]()
    print(rules)
