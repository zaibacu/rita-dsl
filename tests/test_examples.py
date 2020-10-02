import pytest

import rita

from utils import spacy_engine, standalone_engine, rust_engine, load_rules


@pytest.fixture(scope="session")
def bench_text():
    # TODO: think of new case for testing
    pass


@pytest.mark.parametrize('engine', [spacy_engine])
def test_color_car(engine):
    text = "John Silver was driving a red car. It was BMW X6 Mclass. John likes driving it very much."
    parser = engine(load_rules("examples/color-car.rita"))
    entities = set(parser(text))
    print(entities)

    expected = set([
        ("John Silver", "PERSON"),       # Normal NER
        ("red car", "CAR_COLOR"),        # Our first rule
        ("BMW X6 Mclass", "CAR_MODEL"),  # Our second rule
        ("John likes driving", "LIKED_ACTION")  # Our third rule
    ])

    assert entities.issuperset(expected)


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_fuzzy_matching(engine):
    parser = engine("""
    !IMPORT("rita.modules.fuzzy")

    FUZZY("squirrel") -> MARK("CRITTER")
    """)

    # Check if we're matching with capitalized word
    t1 = """
    Squirrel just walked outside
    """

    entities = parser(t1)

    assert len(entities) == 1
    assert entities[0] == ("Squirrel", "CRITTER")

    # Check if we're matching with all CAPS
    t2 = """
    there's a SQUIRREL
    """

    entities = parser(t2)

    assert len(entities) == 1
    assert entities[0] == ("SQUIRREL", "CRITTER")


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_election(engine):
    parser = engine(
        """
        {ENTITY("PERSON")+, WORD("was"), WORD("elected")}->MARK("WON_ELECTION")
        {WORD("defeating"), ENTITY("PERSON")+}->MARK("LOST_ELECTION")
        """
    )
    text = "Donald Trump was elected President in 2016 defeating Hilary Clinton."

    entities = set(parser(text))
    expected = set([
        ("Donald Trump was elected", "WON_ELECTION"),
        ("defeating Hilary Clinton", "LOST_ELECTION"),
    ])
    print(entities)

    assert entities.issuperset(expected)


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_dash_case(engine):
    parser = engine(load_rules("examples/dress-match.rita"))
    text = """
    Fitted, knee-length dress in soft velour
    """

    entities = set(parser(text))
    print(entities)
    expected = set([
        ("Fitted, knee-length dress", "DRESS_TYPE"),
        ("soft velour", "DRESS_FABRIC"),
    ])

    assert entities.issuperset(expected)


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_exclude_word(engine):
    # Rust engine doesn't work here, because Re2 doesn't support backtracking operator
    parser = engine(load_rules("examples/excluding-word.rita"))

    t1 = "Weather is awesome"
    t2 = "Weather is cold"

    r1 = parser(t1)
    r2 = parser(t2)

    assert r1[0] == ("Weather is awesome", "GOOD_WEATHER")
    assert len(r2) == 0


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_escape_string(engine):
    # If it compiles - good enough
    engine(load_rules("examples/match-with-escaped-string.rita"))


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_case_sensitive(engine):
    parser = engine(
        """
        !CONFIG("ignore_case", "N")

        variants = {"Bitcoin", "BTC", "Bitcoin Cash"}

        {IN_LIST(variants)}->MARK("CRYPTO")
        """
    )

    text = """
    A bitcoin mining magnate has proposed a new development fund for Bitcoin Cash.
    According to BTC.TOP CEO Jiang Zhuoer, the scheme will 'tax' Bitcoin Cash mining rewards
    in an effort to increase funding for Bitcoin Cash infrastructure.
    """

    results = parser(text)
    print(results)
    filtered = list([r
                    for r in results
                    if r[1] == "CRYPTO"])

    assert len(filtered) > 0
    assert filtered[0] == ("Bitcoin Cash", "CRYPTO")


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_with_implicit_hyphon(engine):
    parser = engine(
        """
        !CONFIG("implicit_punct", "N")
        !CONFIG("implicit_hyphon", "Y")
        {WORD("Hello"), WORD("World")}->MARK("HYPHON_LABEL")
        WORD("Hello")->MARK("HELLO_LABEL")
        """
    )

    text = "Hello - world!"
    results = parser(text)
    print(results)

    assert len(results) == 1
    assert results[0] == ("Hello - world", "HYPHON_LABEL")


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_without_implicit_hyphon(engine):
    parser = engine(
        """
        !CONFIG("implicit_punct", "N")
        !CONFIG("implicit_hyphon", "N")
        {WORD("Hello"), WORD("World")}->MARK("HYPHON_LABEL")
        WORD("Hello")->MARK("HELLO_LABEL")
        """
    )

    text = "Hello - world!"
    results = parser(text)
    print(results)

    assert len(results) == 1
    assert results[0] == ("Hello", "HELLO_LABEL")


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_prefix(engine):
    parser = engine(
        """
        science = {"mathematics", "physics"}
        {PREFIX("meta"), IN_LIST(science)}->MARK("META_SCIENCE")
        {PREFIX("pseudo"), WORD("science")}->MARK("PSEUDO_SCIENCE")
        """
    )

    text = """
    This paper is full of metaphysics and pseudoscience
    """

    results = parser(text)
    print(results)
    assert results[0] == ("metaphysics", "META_SCIENCE")
    assert results[1] == ("pseudoscience", "PSEUDO_SCIENCE")


@pytest.mark.parametrize('engine', ["standalone", "rust"])
def test_compile_context(engine):
    if engine == "rust":
        from rita.engine.translate_rust import load_lib
        lib = load_lib()
        if lib is None:
            pytest.skip("Missing rita-rust dynamic lib, skipping related tests")
    rules = """

    {WORD*, IN_LIST(companies), WORD*}->MARK("SUSPISCIOUS_COMPANY")
    """
    parser = rita.compile_string(rules, use_engine=engine, companies=["CompanyA", "CompanyB"])
    print(parser.patterns)

    results = list(parser.execute("CompanyB is doing it's dirty work."))
    assert results[0] == {
        "start": 0,
        "end": 33,
        "label": "SUSPISCIOUS_COMPANY",
        "text": "CompanyB is doing it's dirty work",
        "submatches": [
            {
                "start": 0,
                "end": 33,
                "key": "SUSPISCIOUS_COMPANY",
                "text": "CompanyB is doing it's dirty work"
            },
            {
                "start": 0,
                "end": 9,
                "key": "s2",
                "text": "CompanyB"
            },
            {
                "start": 9,
                "end": 33,
                "key": "s4",
                "text": "is doing it's dirty work"
            }
        ],
    }


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_benchmark(benchmark, engine, bench_text):
    """
    These tests will only run if parameters:
    `--benchmark-enable` or
    `--benchmark-only`
    are added
    """
    parser = engine(load_rules("examples/cheap-phones.rita"))

    def parse_rows(parser, rows):
        for r in rows:
            parser(r)

    benchmark.pedantic(
        parse_rows,
        args=(parser, bench_text),
        iterations=3,
        rounds=3
    )


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_variable_pattern(engine):
    parser = engine("""
    Complex_Number = { NUM+, WORD("/")?, NUM? }
    {PATTERN(Complex_Number), WORD("inches"), WORD("Width")}->MARK("WIDTH")
    {PATTERN(Complex_Number), WORD("inches"), WORD("Height")}->MARK("HEIGHT")
    """)
    text = """
        It is 17 1/2 inches width and 10 inches height
        """

    results = parser(text)
    assert len(results) == 2


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine, rust_engine])
def test_inlist_longest(engine):
    parser = engine("""
    units = {"m", "mm", "cm"}
    dimensions = {"width", "height", "length"}
    {IN_LIST(dimensions), NUM, IN_LIST(units)}->MARK("TEST")
    """)

    text = """
    width 10 mm
    """

    results = parser(text)

    assert len(results) == 1
    (result, label) = results[0]
    assert result == "width 10 mm"


@pytest.mark.parametrize('engine', [standalone_engine, rust_engine])
def test_inlist_word_based(engine):
    parser = engine("""
    units = {"m", "mm", "cm", "inches", "in"}
    {IN_LIST(units), NUM}->MARK("TEST")
    """)

    text = """
    twin 20 turbo
    """

    results = parser(text)
    print(results)
    assert len(results) == 0


@pytest.mark.parametrize('engine', [standalone_engine, spacy_engine, rust_engine])
def test_pluralize(engine):
    pytest.importorskip("inflect")
    parser = engine("""
    !IMPORT("rita.modules.pluralize")

    vehicles={"car", "motorbike", "bicycle", "ship", "plane"}
    {NUM, PLURALIZE(vehicles)}->MARK("VEHICLES")
    """)

    text = """
    There were 7 cars, 2 motorbikes, 1 ship, 1 bicycle and 9 planes
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "VEHICLES"])
    print(results)

    assert len(results) == 5
    assert {"7 cars", "2 motorbikes", "1 ship", "1 bicycle", "9 planes"} == results


@pytest.mark.parametrize('engine', [spacy_engine])
def test_orth_example(engine):
    parser = engine("""
    !IMPORT("rita.modules.orth")

    {ORTH("IEEE")}->MARK("TAGGED_MATCH")
    """)

    text = """
    it should match IEEE, but should ignore ieee
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "TAGGED_MATCH"])

    print(results)
    assert len(results) == 1
    assert {"IEEE"} == results


@pytest.mark.parametrize('engine', [standalone_engine, spacy_engine, rust_engine])
def test_regex_module_start(engine):
    parser = engine("""
    !IMPORT("rita.modules.regex")

    {REGEX("^a")}->MARK("TAGGED_MATCH")
    """)

    text = """
    there are many letters in the alphabet
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "TAGGED_MATCH"])

    print(results)
    assert len(results) == 2
    assert {"are", "alphabet"} == results


@pytest.mark.parametrize('engine', [standalone_engine, spacy_engine, rust_engine])
def test_regex_module_end(engine):
    parser = engine("""
    !IMPORT("rita.modules.regex")

    {REGEX("e$")}->MARK("TAGGED_MATCH")
    """)

    text = """
    there are many letters in the alphabet
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "TAGGED_MATCH"])

    print(results)
    assert len(results) == 3
    assert {"there", "are", "the"} == results


@pytest.mark.parametrize('engine', [standalone_engine, spacy_engine, rust_engine])
def test_regex_module_middle(engine):
    parser = engine("""
    !IMPORT("rita.modules.regex")

    {REGEX("et")}->MARK("TAGGED_MATCH")
    """)

    text = """
    there are many letters in the alphabet
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "TAGGED_MATCH"])

    print(results)
    assert len(results) == 2
    assert {"letters", "alphabet"} == results


@pytest.mark.parametrize('engine', [standalone_engine, spacy_engine, rust_engine])
def test_regex_module_strict(engine):
    parser = engine("""
    !IMPORT("rita.modules.regex")

    {REGEX("^the$")}->MARK("TAGGED_MATCH")
    """)

    text = """
    there are many letters in the alphabet
    """

    results = set([text
                   for text, label in parser(text)
                   if label == "TAGGED_MATCH"])

    print(results)
    assert len(results) == 1
    assert {"the"} == results


@pytest.mark.parametrize('engine', [standalone_engine])
def test_custom_regex_impl(engine):
    import re

    class MyMatch(object):
        def __init__(self, result):
            self.result = result

        def start(self):
            return 0

        def end(self):
            return len(self.result)

        def group(self):
            return self.result

        def groupdict(self):
            return {}

        @property
        def lastgroup(self):
            return "TEST_MATCH"

    class MyCustomRegex(object):
        DOTALL = re.DOTALL
        IGNORECASE = re.IGNORECASE

        def compile(self, *args, **kwargs):
            return self

        def match(self, *args, **kwargs):
            return self

        def search(self, *args, **kwargs):
            return self

        def finditer(self, text):
            return [MyMatch("Hello new REGEX")]

    parser = engine("""
    {WORD("Hello"), WORD("new"), WORD("regex")}->MARK("TEST_MATCH")
    """, regex_impl=MyCustomRegex())

    results = parser("Hello new REGEX!")

    assert len(results) == 1


@pytest.mark.parametrize('engine', [standalone_engine, rust_engine])
def test_complex_number_match(engine):
    parser = engine("""
    fractions={"1 / 2", "3 / 4", "1 / 8", "3 / 8", "5 / 8", "7 / 8", "1 / 16", "3 / 16", "5 / 16", "7 / 16", "9 / 16",
    "11 / 16", "13 / 16", "15 / 16", "1 / 32", "3 / 32", "5 / 32", "7 / 32", "9 / 32", "11 / 32", "13 / 32", "15 / 32",
    "17 / 32", "19 / 32", "21 / 32", "23 / 32", "25 / 32", "27 / 32", "29 / 32", "31 / 32"}

    num_with_fractions = {NUM, WORD("-")?, IN_LIST(fractions)}
    complex_number = {NUM|PATTERN(num_with_fractions)}

    {WORD("length"), PATTERN(complex_number)}->MARK("NUMBER")
    """)

    simple_number = parser("length 50 cm")
    assert len(simple_number) == 1
    assert ("length 50", "NUMBER") == simple_number[0]

    complex_number = parser('length 10 1 / 2 "')

    assert len(complex_number) == 1
    assert ("length 10 1 / 2", "NUMBER") == complex_number[0]


@pytest.mark.parametrize('engine', [standalone_engine, rust_engine])
def test_simple_float_number_match(engine):
    parser = engine("""
    NUM->MARK("NUMBER")
    """)

    assert parser("25")[0] == ("25", "NUMBER")
    assert parser("25.7")[0] == ("25.7", "NUMBER")
    assert parser("19,6")[0] == ("19,6", "NUMBER")


@pytest.mark.parametrize('engine', [standalone_engine, rust_engine])
def test_invalid_entity(engine):
    with pytest.raises(RuntimeError):
        engine("""
        ENTITY("ORG")->MARK("ORG_MATCH")
        """)
