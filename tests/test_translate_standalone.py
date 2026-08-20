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
