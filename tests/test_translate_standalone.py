import os
import tempfile

import pytest

import rita

from rita.engine.translate_standalone import (
    RuleExecutor,
    RuleCompileError,
    escape_literal,
    regex_parse,
)
from rita.utils import ExtendedOp


def compile_rules(rules, **kwargs):
    return rita.compile_string(rules, use_engine="standalone", **kwargs)


class TestEscapeLiteral:
    def test_escapes_bare_metachars(self):
        assert escape_literal("C++") == r"C\+\+"
        assert escape_literal("a.b") == r"a\.b"
        assert escape_literal("foo(bar") == r"foo\(bar"

    def test_keeps_already_escaped_sequences(self):
        # eg. rita.modules.names generates values like `J\.`
        assert escape_literal(r"J\. Smith") == r"J\. Smith"

    def test_plain_words_unchanged(self):
        assert escape_literal("hello") == "hello"
        assert escape_literal("knee-length") == "knee-length"


class TestLiteralEscaping:
    def test_word_with_metachars_matches_literally(self):
        parser = compile_rules('{WORD("C++")}->MARK("LANG")')
        results = list(parser.execute("I code in C++ daily"))
        assert len(results) == 1
        assert results[0]["text"] == "C++"

    def test_word_with_metachars_does_not_wildcard(self):
        parser = compile_rules('{WORD("C++")}->MARK("LANG")')
        assert list(parser.execute("plain c code")) == []

    def test_list_with_metachars(self):
        parser = compile_rules('items = {"a.b", "c+d"}\n{IN_LIST(items)}->MARK("X")')
        results = list(parser.execute("value a.b and axb here"))
        assert [r["text"] for r in results] == ["a.b"]

    def test_word_with_unbalanced_paren(self):
        parser = compile_rules('{WORD("foo(bar")}->MARK("X")')
        results = list(parser.execute("foo(bar test"))
        assert len(results) == 1
        assert results[0]["text"] == "foo(bar"

    def test_single_item_list_is_not_split_into_characters(self):
        parser = compile_rules('items = {"a.b"}\n{IN_LIST(items)}->MARK("X")')
        results = list(parser.execute("value a.b and axb here"))
        assert [r["text"] for r in results] == ["a.b"]


class TestCompileErrors:
    def test_invalid_label_raises_at_compile_time(self):
        with pytest.raises(RuleCompileError, match="MY-LABEL"):
            compile_rules('{WORD("hi")}->MARK("MY-LABEL")')

    def test_empty_regex_raises(self):
        with pytest.raises(RuleCompileError):
            regex_parse("", None, ExtendedOp(None))


class TestNegation:
    def test_negated_list_matches_word_outside_list(self):
        parser = compile_rules('lst = {"cat", "dog"}\n{WORD("no"), IN_LIST(lst)!}->MARK("X")')
        assert len(list(parser.execute("no bird here"))) == 1

    def test_negated_list_rejects_word_in_list(self):
        parser = compile_rules('lst = {"cat", "dog"}\n{WORD("no"), IN_LIST(lst)!}->MARK("X")')
        assert list(parser.execute("no cat here")) == []

    def test_negated_word(self):
        parser = compile_rules('{WORD("no"), WORD("cat")!}->MARK("X")')
        assert len(list(parser.execute("no bird"))) == 1
        assert list(parser.execute("no cat")) == []


class TestSaveLoad:
    def test_round_trip_preserves_case_sensitivity(self):
        parser = compile_rules('!CONFIG("ignore_case", "F")\n{WORD("Hello")}->MARK("X")')
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            parser.save(path)
            loaded = RuleExecutor.load(path)
            assert list(loaded.execute("hello")) == []
            assert len(list(loaded.execute("Hello"))) == 1
        finally:
            os.unlink(path)

    def test_legacy_headerless_file_loads(self):
        parser = compile_rules('{WORD("Hello")}->MARK("X")')
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            parser.save(path)
            with open(path, "r") as f:
                lines = f.readlines()
            with open(path, "w") as f:
                f.writelines([line for line in lines if "config" not in line])
            loaded = RuleExecutor.load(path)
            assert len(list(loaded.execute("hello"))) == 1
        finally:
            os.unlink(path)

    def test_malformed_line_raises_with_line_number(self):
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            with open(path, "w") as f:
                f.write("not json\n")
            with pytest.raises(ValueError, match="line 1"):
                RuleExecutor.load(path)
        finally:
            os.unlink(path)


class TestExecution:
    def test_tie_breaking_is_deterministic(self):
        rules = '{WORD("t")}->MARK("A")\n{WORD("t")}->MARK("B")'
        labels = set()
        for _ in range(20):
            parser = compile_rules(rules)
            labels.add(list(parser.execute("a t here"))[0]["label"])
        assert labels == {"A"}

    def test_match_timeout_with_stdlib_re_raises_clear_error(self):
        parser = compile_rules('{WORD("hi")}->MARK("X")', match_timeout=1)
        with pytest.raises(RuntimeError, match="regex"):
            list(parser.execute("hi"))

    def test_match_timeout_with_regex_module(self):
        regex = pytest.importorskip("regex")
        parser = compile_rules(
            '!IMPORT("rita.modules.regex")\n{REGEX("(a|aa)+$")}->MARK("BOOM")',
            regex_impl=regex,
            match_timeout=0.5,
        )
        with pytest.raises(TimeoutError):
            list(parser.execute("a" * 40 + "b"))


class TestOperators:
    def test_one_or_more(self):
        parser = compile_rules('{WORD("very")+, WORD("good")}->MARK("X")')
        results = list(parser.execute("it is very very very good indeed"))
        assert [r["text"] for r in results] == ["very very very good"]

    def test_zero_or_more(self):
        parser = compile_rules('{WORD("a"), WORD("b")*}->MARK("X")')
        assert [r["text"] for r in parser.execute("a b b b")] == ["a b b b"]
        assert len(list(parser.execute("just a alone"))) == 1

    def test_optional(self):
        parser = compile_rules('{WORD("a"), WORD("b")?, WORD("c")}->MARK("X")')
        assert len(list(parser.execute("a b c"))) == 1
        assert len(list(parser.execute("a c"))) == 1
        assert list(parser.execute("a x c")) == []

    def test_optional_list(self):
        parser = compile_rules('sizes = {"small", "big"}\n'
                               '{IN_LIST(sizes)?, WORD("dog")}->MARK("X")')
        assert [r["text"] for r in parser.execute("a big dog")] == ["big dog"]
        assert [r["text"] for r in parser.execute("a dog")] == ["dog"]


class TestGenericTokens:
    def test_word_without_args_matches_any_word(self):
        parser = compile_rules('{WORD, WORD("runs")}->MARK("X")')
        assert [r["text"] for r in parser.execute("dog runs")] == ["dog runs"]

    def test_num_without_args(self):
        parser = compile_rules('{NUM}->MARK("N")')
        assert [r["text"] for r in parser.execute("pi is 3.14 ok")] == ["3.14"]

    def test_num_literal(self):
        parser = compile_rules('{NUM("42")}->MARK("N")')
        assert [r["text"] for r in parser.execute("answer is 42")] == ["42"]

    def test_any_matches_gap(self):
        parser = compile_rules('{WORD("start"), ANY, WORD("end")}->MARK("X")')
        assert [r["text"] for r in parser.execute("start middle end")] == ["start middle end"]

    def test_explicit_punct(self):
        parser = compile_rules('{WORD("a"), PUNCT, WORD("b")}->MARK("X")')
        assert [r["text"] for r in parser.execute("a , b")] == ["a , b"]

    def test_entity_person(self):
        parser = compile_rules('{ENTITY("PERSON")}->MARK("P")')
        results = list(parser.execute("Met John yesterday"))
        assert "John" in [r["text"] for r in results]


class TestPreprocessing:
    def test_deaccent_matches_both_forms(self):
        parser = compile_rules('{WORD("naïve")}->MARK("X")')
        assert len(list(parser.execute("naive approach"))) == 1
        assert len(list(parser.execute("naïve approach"))) == 1

    def test_multi_word_literal(self):
        parser = compile_rules('{WORD("New York")}->MARK("CITY")')
        assert [r["text"] for r in parser.execute("in New York now")] == ["New York"]

    def test_hyphenated_word(self):
        parser = compile_rules('{WORD("knee-length")}->MARK("X")')
        assert [r["text"] for r in parser.execute("a knee-length dress")] == ["knee-length"]

    def test_or_branching(self):
        parser = compile_rules('{WORD("cat")|WORD("dog")}->MARK("PET")')
        assert [r["text"] for r in parser.execute("a dog here")] == ["dog"]
        assert [r["text"] for r in parser.execute("a cat here")] == ["cat"]

    def test_prefix_on_word(self):
        parser = compile_rules('{PREFIX("mega"), WORD("byte")}->MARK("X")')
        assert [r["text"] for r in parser.execute("a megabyte here")] == ["megabyte"]
        assert list(parser.execute("a byte here")) == []

    def test_prefix_on_list(self):
        parser = compile_rules('science = {"physics", "biology"}\n'
                               '{PREFIX("meta"), IN_LIST(science)}->MARK("X")')
        assert [r["text"] for r in parser.execute("study metaphysics now")] == ["metaphysics"]


class TestUnsupportedRules:
    @pytest.mark.parametrize("rules,name", [
        ('{ENTITY("ORG")}->MARK("E")', "ORG"),
        ('{LEMMA("be")}->MARK("L")', "LEMMA"),
        ('{POS("NOUN")}->MARK("P")', "POS"),
        ('!IMPORT("rita.modules.tag")\n{TAG("^NN")}->MARK("T")', "TAG"),
        ('!IMPORT("rita.modules.orth")\n{ORTH("Test")}->MARK("O")', "ORTH"),
    ])
    def test_unsupported_rule_raises_clear_error(self, rules, name):
        # Must be a helpful RuntimeError, not a bare KeyError
        with pytest.raises(RuntimeError, match=name):
            compile_rules(rules)


class TestMatchSemantics:
    def test_longest_match_wins_at_same_start(self):
        parser = compile_rules('{WORD("New")}->MARK("SHORT")\n'
                               '{WORD("New"), WORD("York")}->MARK("LONG")')
        results = list(parser.execute("in New York now"))
        assert [r["label"] for r in results] == ["LONG"]

    def test_submatch_offsets_point_into_text(self):
        text = "the answer is 42 indeed"
        parser = compile_rules('{WORD("is"), NUM}->MARK("X")')
        (result,) = parser.execute(text)
        assert text[result["start"]:result["end"]].strip() == result["text"]
        for sub in result["submatches"]:
            assert text[sub["start"]:sub["end"]].strip() == sub["text"]

    def test_include_submatches_false(self):
        parser = compile_rules('{WORD("a"), WORD("b")}->MARK("X")')
        (result,) = parser.execute("a b", include_submatches=False)
        assert result["submatches"] == []

    def test_multiple_occurrences(self):
        parser = compile_rules('{WORD("dog")}->MARK("PET")')
        results = list(parser.execute("dog meets dog and dog"))
        assert len(results) == 3
        assert [r["text"] for r in results] == ["dog", "dog", "dog"]

    def test_case_insensitive_by_default(self):
        parser = compile_rules('{WORD("Hello")}->MARK("X")')
        assert len(list(parser.execute("HELLO hello HeLLo"))) == 3

    def test_case_sensitive_via_config(self):
        parser = compile_rules('!CONFIG("ignore_case", "F")\n{WORD("Hello")}->MARK("X")')
        assert [r["text"] for r in parser.execute("hello Hello HELLO")] == ["Hello"]

    def test_multiline_text(self):
        parser = compile_rules('{WORD("a"), WORD("b")}->MARK("X")')
        assert len(list(parser.execute("a\nb"))) == 1

    def test_unicode_word(self):
        parser = compile_rules('{WORD("žodis")}->MARK("X")')
        assert [r["text"] for r in parser.execute("lietuviškas žodis čia")] == ["žodis"]

    def test_empty_text(self):
        parser = compile_rules('{WORD("a")}->MARK("X")')
        assert list(parser.execute("")) == []

    def test_empty_ruleset(self):
        parser = compile_rules('')
        assert list(parser.execute("any text at all")) == []


class TestAnchor:
    def test_before_anchor_required_but_excluded(self):
        parser = compile_rules('{ANCHOR(WORD("price")), NUM}->MARK("VALUE")')
        (result,) = parser.execute("the price 42 is fine")
        assert result["text"] == "42"
        assert "price" not in result["text"]
        # anchor is required context
        assert list(parser.execute("just 42 here")) == []

    def test_after_anchor(self):
        parser = compile_rules('cur = {"eur", "usd"}\n'
                               '{NUM, ANCHOR(IN_LIST(cur))}->MARK("AMOUNT")')
        (result,) = parser.execute("it costs 42 eur now")
        assert result["text"] == "42"
        assert list(parser.execute("42 bananas")) == []

    def test_anchors_on_both_sides(self):
        parser = compile_rules('{ANCHOR(WORD("from")), NUM, ANCHOR(WORD("to"))}->MARK("X")')
        (result,) = parser.execute("go from 5 to 9")
        assert result["text"] == "5"

    def test_span_points_into_text(self):
        text = "price: 42"
        parser = compile_rules('{ANCHOR(WORD("price")), NUM}->MARK("VALUE")')
        (result,) = parser.execute(text)
        assert text[result["start"]:result["end"]].strip() == "42"

    def test_submatches_exclude_anchor_groups(self):
        parser = compile_rules('{ANCHOR(WORD("price")), NUM}->MARK("VALUE")')
        (result,) = parser.execute("price 42")
        for sub in result["submatches"]:
            assert not sub["key"].startswith("a")

    def test_multiple_leading_anchors(self):
        parser = compile_rules('{ANCHOR(WORD("total")), ANCHOR(WORD("price")), NUM}->MARK("X")')
        (result,) = parser.execute("total price 42")
        assert result["text"] == "42"
        assert list(parser.execute("price 42")) == []

    def test_anchor_with_operator(self):
        parser = compile_rules('{ANCHOR(WORD("price")?), NUM, ANCHOR(WORD("eur"))}->MARK("X")')
        assert [r["text"] for r in parser.execute("price 42 eur")] == ["42"]
        assert [r["text"] for r in parser.execute("42 eur")] == ["42"]

    def test_amp_shortcut_equivalent_to_anchor_macro(self):
        import re as _re
        explicit = compile_rules('{ANCHOR(WORD("price")), NUM}->MARK("X")')
        shortcut = compile_rules('{&WORD("price"), NUM}->MARK("X")')

        def norm(pattern):
            # anchor group ids come from a session-wide counter
            return _re.sub(r"a\d+", "aN", pattern)

        assert norm(explicit.patterns[0].pattern) == norm(shortcut.patterns[0].pattern)

    def test_amp_shortcut_before_and_after(self):
        parser = compile_rules('{&WORD("from"), NUM, &WORD("to")}->MARK("X")')
        (result,) = parser.execute("go from 5 to 9")
        assert result["text"] == "5"
        assert list(parser.execute("just 5 here")) == []

    def test_amp_shortcut_with_modifier(self):
        parser = compile_rules('{&WORD("price")?, NUM, &WORD("eur")}->MARK("X")')
        assert [r["text"] for r in parser.execute("price 42 eur")] == ["42"]
        assert [r["text"] for r in parser.execute("42 eur")] == ["42"]

    def test_amp_shortcut_with_list(self):
        parser = compile_rules('cur = {"eur", "usd"}\n{NUM, &IN_LIST(cur)}->MARK("A")')
        assert [r["text"] for r in parser.execute("worth 42 usd")] == ["42"]

    def test_mid_pattern_anchor_raises(self):
        with pytest.raises(RuleCompileError, match="start or"):
            compile_rules('{WORD("a"), ANCHOR(WORD("b")), WORD("c")}->MARK("X")')

    def test_anchor_only_rule_raises(self):
        with pytest.raises(RuleCompileError, match="only of ANCHOR"):
            compile_rules('{ANCHOR(WORD("a"))}->MARK("X")')

    def test_anchor_inside_pattern_raises(self):
        with pytest.raises((RuleCompileError, ValueError)):
            compile_rules('p = {ANCHOR(WORD("a")), WORD("b")}\n'
                          '{PATTERN(p), WORD("c")}->MARK("X")')

    def test_save_load_round_trip_keeps_anchors(self):
        parser = compile_rules('{ANCHOR(WORD("price")), NUM}->MARK("VALUE")')
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            parser.save(path)
            loaded = RuleExecutor.load(path)
            (result,) = loaded.execute("price 42")
            assert result["text"] == "42"
            assert list(loaded.execute("42")) == []
        finally:
            os.unlink(path)


class TestAnchorRustEngine:
    @pytest.fixture(autouse=True)
    def _require_lib(self):
        from rita.engine.translate_rust import load_lib
        if load_lib() is None:
            pytest.skip("Missing rita-rust dynamic lib")

    def test_before_and_after_anchor(self):
        import rita
        parser = rita.compile_string(
            '{ANCHOR(WORD("price")), NUM, ANCHOR(WORD("eur"))}->MARK("X")',
            use_engine="rust")
        (result,) = parser.execute("price 42 eur")
        assert result["text"] == "42"
        assert list(parser.execute("42 eur")) == []
        for sub in result["submatches"]:
            assert not sub["key"].startswith("a")


class TestRuleExecutorAPI:
    def test_iter_yields_labeled_rules(self):
        parser = compile_rules('{WORD("a")}->MARK("X")\n{WORD("b")}->MARK("Y")')
        exported = list(parser)
        assert [e["label"] for e in exported] == ["X", "Y"]
        for e in exported:
            assert isinstance(e["rules"], list)

    def test_save_load_round_trip_preserves_patterns(self):
        parser = compile_rules('lst = {"a", "b"}\n{WORD("x"), IN_LIST(lst)}->MARK("X")')
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            parser.save(path)
            loaded = RuleExecutor.load(path)
            assert list(loaded) == list(parser)
        finally:
            os.unlink(path)

    def test_load_missing_file(self):
        with pytest.raises(FileNotFoundError):
            RuleExecutor.load("/nonexistent/rules.jsonl")

    def test_load_unexpected_object_raises(self):
        path = tempfile.mktemp(suffix=".jsonl")
        try:
            with open(path, "w") as f:
                f.write('{"foo": "bar"}\n')
            with pytest.raises(ValueError, match="Unexpected object"):
                RuleExecutor.load(path)
        finally:
            os.unlink(path)
