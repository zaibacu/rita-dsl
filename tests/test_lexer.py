from rita.lexer import RitaLexer


def test_tokenize_any_macro_wo_args_wo_type():
    lex = RitaLexer()
    lex.build()

    tokens = list(lex.tokenize("ANY"))
    assert len(tokens) == 1
    token = tokens[0]
    assert token.type == "KEYWORD"
    assert token.value == "ANY"


def test_tokenize_any_macro_wo_args_w_type():
    lex = RitaLexer()
    lex.build()

    tokens = list(lex.tokenize('ANY -> MARK{"Placeholder"}'))
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
    lex = RitaLexer()
    lex.build()

    tokens = list(lex.tokenize('Test = "Test"'))

    assert len(tokens) == 3

    assert tokens[0].type == "NAME"
    assert tokens[1].type == "ASSIGN"
    assert tokens[2].type == "LITERAL"


def test_tokenize_assign_macro():
    lex = RitaLexer()
    lex.build()

    tokens = list(lex.tokenize('Test = WORD{"Test"}'))

    assert len(tokens) == 6

    assert tokens[0].type == "NAME"
    assert tokens[1].type == "ASSIGN"
    assert tokens[2].type == "KEYWORD"
    assert tokens[4].type == "LITERAL"


def test_tokenize_exec_macro():
    lex = RitaLexer()
    lex.build()
    tokens = list(lex.tokenize('!IMPORT("module.test")'))
    assert len(tokens) == 5
    assert tokens[0].type == "EXEC"
    assert tokens[1].type == "KEYWORD"
    assert tokens[3].type == "LITERAL"


def test_tokenize_two_exec_macros():
    lex = RitaLexer()
    lex.build()
    tokens = list(
        lex.tokenize(
            """
            !CONFIG("setting.1", "1")
            !CONFIG("setting.2", "0")
            """
        )
    )
    assert len(tokens) == 14
    assert tokens[0].type == "EXEC"
    assert tokens[1].type == "KEYWORD"
    assert tokens[3].type == "LITERAL"
    assert tokens[5].type == "LITERAL"

    assert tokens[7].type == "EXEC"
    assert tokens[8].type == "KEYWORD"
    assert tokens[10].type == "LITERAL"
    assert tokens[12].type == "LITERAL"


def test_tokenize_list_w_one_item():
    lex = RitaLexer()
    lex.build()

    tokens = list(
        lex.tokenize(
            """
            MEMBERS = { "first" }
            """
        )
    )

    assert tokens[0].type == "KEYWORD"
    assert tokens[1].type == "ASSIGN"
    assert tokens[3].type == "LITERAL"
