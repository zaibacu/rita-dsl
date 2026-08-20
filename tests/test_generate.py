import os
import tempfile

import pytest

import rita

from rita.generate import (
    tokenize,
    generate,
    minimize_rules,
    collect_rules,
    escape,
    main,
    Token,
)


def write_csv(rows, header=True):
    path = tempfile.mktemp(suffix=".csv")
    with open(path, "w", encoding="UTF-8") as f:
        if header:
            f.write("text,span,label\n")
        for row in rows:
            f.write(",".join('"{}"'.format(c.replace('"', '""')) for c in row) + "\n")
    return path


class TestTokenize:
    def test_words(self):
        assert tokenize("red car") == [Token("word", "red"), Token("word", "car")]

    def test_numbers(self):
        assert tokenize("42 eur") == [Token("num", "42"), Token("word", "eur")]
        assert tokenize("3.14") == [Token("num", "3.14")]

    def test_punct(self):
        assert tokenize("a, b") == [Token("word", "a"), Token("punct", ","), Token("word", "b")]

    def test_hyphenated_word_is_one_token(self):
        assert tokenize("knee-length") == [Token("word", "knee-length")]


class TestMerging:
    def test_same_shape_merges_into_one_rule(self):
        errors = []
        rows = [(i, ["t", span, "FRUIT"]) for i, span in enumerate(["apples", "oranges", "plums"], 1)]
        rows = [(line, [span, span, label]) for (line, (_, span, label)) in rows]
        rules = minimize_rules(collect_rules(rows, errors))
        assert len(rules) == 1
        assert list(rules[0].slots[0].values) == ["apples", "oranges", "plums"]

    def test_extra_token_becomes_optional(self):
        errors = []
        rows = [
            (1, ["big red car", "big red car", "VEHICLE"]),
            (2, ["red car", "red car", "VEHICLE"]),
        ]
        rules = minimize_rules(collect_rules(rows, errors))
        assert len(rules) == 1
        assert rules[0].slots[0].optional is True
        assert rules[0].slots[1].optional is False

    def test_different_labels_stay_separate(self):
        errors = []
        rows = [
            (1, ["apples", "apples", "FRUIT"]),
            (2, ["hammer", "hammer", "TOOL"]),
        ]
        rules = minimize_rules(collect_rules(rows, errors))
        assert len(rules) == 2

    def test_values_dedup_case_insensitive(self):
        errors = []
        rows = [
            (1, ["Apples", "Apples", "FRUIT"]),
            (2, ["apples", "apples", "FRUIT"]),
        ]
        rules = minimize_rules(collect_rules(rows, errors))
        assert len(list(rules[0].slots[0].values)) == 1


class TestEscape:
    def test_quotes_and_backslashes(self):
        assert escape('say "hi"') == 'say \\"hi\\"'
        assert escape("a\\b") == "a\\\\b"


class TestGenerate:
    def test_full_coverage(self):
        path = write_csv([
            ("I really like apples", "apples", "FRUIT"),
            ("She likes oranges a lot", "oranges", "FRUIT"),
            ("The price is 42 eur today", "42 eur", "AMOUNT"),
            ("It costs 7 usd", "7 usd", "AMOUNT"),
        ])
        try:
            source, errors, misses = generate(path)
            assert errors == []
            assert misses == []
            # minimality: 4 rows -> 2 rules
            assert sum(1 for line in source.splitlines() if "->MARK(" in line) == 2
        finally:
            os.unlink(path)

    def test_generated_rules_compile_and_match(self):
        path = write_csv([
            ("we sell milk here", "milk", "PRODUCT"),
            ("we sell bread here", "bread", "PRODUCT"),
        ])
        try:
            source, _, misses = generate(path)
            assert misses == []
            parser = rita.compile_string(source, use_engine="standalone")
            # generalization: merged list matches either value in new text
            results = list(parser.execute("bread and milk on the table"))
            assert {r["text"] for r in results} == {"bread", "milk"}
        finally:
            os.unlink(path)

    def test_number_generalization(self):
        path = write_csv([
            ("total 42 eur", "42 eur", "AMOUNT"),
            ("total 7 eur", "7 eur", "AMOUNT"),
        ])
        try:
            source, _, misses = generate(path)
            assert misses == []
            parser = rita.compile_string(source, use_engine="standalone")
            # generic NUM matches unseen numbers
            (result,) = parser.execute("total 123 eur")
            assert result["text"] == "123 eur"
        finally:
            os.unlink(path)

    def test_bad_rows_are_reported(self):
        path = write_csv([
            ("hello world", "not here", "X"),
            ("hello world", "world", "BAD-LABEL"),
            ("hello world", "", "X"),
            ("ok row", "ok", "X"),
        ])
        try:
            source, errors, misses = generate(path)
            assert len(errors) == 3
            assert misses == []
            assert '{WORD("ok")}->MARK("X")' in source
        finally:
            os.unlink(path)

    def test_no_rules(self):
        path = write_csv([("text", "absent", "X")])
        try:
            source, errors, misses = generate(path)
            assert source is None
            assert len(errors) == 1
        finally:
            os.unlink(path)


class TestCli:
    def test_writes_output_file_and_exits_zero(self):
        csv_path = write_csv([("a fine day", "fine", "MOOD")])
        out_path = tempfile.mktemp(suffix=".rita")
        try:
            code = main(["-f", csv_path, "-o", out_path])
            assert code == 0
            with open(out_path) as f:
                content = f.read()
            assert '->MARK("MOOD")' in content
            # the generated file is loadable by the normal compile path
            parser = rita.compile(out_path, use_engine="standalone")
            assert len(list(parser.execute("a fine day"))) == 1
        finally:
            os.unlink(csv_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_exit_one_on_uncoverable_rows(self):
        csv_path = write_csv([("hello", "nope", "X"), ("hello", "hello", "X")])
        try:
            assert main(["-f", csv_path, "-o", os.devnull]) == 1
        finally:
            os.unlink(csv_path)

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            main(["-f", "/nonexistent/input.csv"])
