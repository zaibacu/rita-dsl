import csv
import pytest

import rita

from utils import spacy_engine, standalone_engine, load_rules


@pytest.fixture(scope="session")
def bench_text():
    with open("benchmarks/reviews-subset.csv", "r", encoding="UTF-8") as f:
        reader = csv.reader(f)
        return list([row[1] for row in reader])


@pytest.mark.parametrize('engine', [spacy_engine])
def test_color_car(engine):
    text = """
    John Silver was driving a red car. It was BMW X6 Mclass.
    John likes driving it very much.
    """
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


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_fuzzy_matching(engine):
    parser = engine(load_rules("examples/fuzzy-matching.rita"))

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


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_election(engine):
    parser = engine(load_rules("examples/simple-match.rita"))
    text = """
    Donald Trump was elected President in 2016 defeating Hilary Clinton.
    """

    entities = set(parser(text))
    expected = set([
        ("Donald Trump was elected", "WON_ELECTION"),
        ("defeating Hilary Clinton", "LOST_ELECTION"),
    ])
    print(entities)

    assert entities.issuperset(expected)


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
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
    parser = engine(load_rules("examples/excluding-word.rita"))

    t1 = "Weather is awesome"
    t2 = "Weather is cold"

    r1 = parser(t1)
    r2 = parser(t2)

    assert r1[0] == ("Weather is awesome", "GOOD_WEATHER")
    assert len(r2) == 0


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
def test_escape_string(engine):
    # If it compiles - good enough
    parser = engine(load_rules("examples/match-with-escaped-string.rita"))


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
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
    assert results[0] == ("Bitcoin Cash", "CRYPTO")


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
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


def test_compile_context():
    rules = """

    {WORD*, IN_LIST(companies), WORD*}->MARK("SUSPISCIOUS_COMPANY")
    """
    parser = rita.compile_string(rules, use_engine="standalone", companies=["CompanyA", "CompanyB"])
    print(parser.patterns)

    results = list(parser.execute("CompanyB is doing it's dirty work."))
    assert results[0] == {
        "start": 0,
        "end": 33,
        "label": "SUSPISCIOUS_COMPANY",
        "text": "CompanyB is doing it's dirty work"
    }


@pytest.mark.parametrize('engine', [spacy_engine, standalone_engine])
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
