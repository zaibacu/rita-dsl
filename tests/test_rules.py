import os.path
import re
import tempfile

import pytest
import rita


class TestSpacy(object):
    @property
    def punct(self):
        return {'IS_PUNCT': True, 'OP': '?'}

    def compiler(self, rules):
        pytest.importorskip("spacy", minversion="2.1")
        return rita.compile_string(rules, use_engine="spacy")

    def test_punct(self):
        rules = self.compiler('PUNCT->MARK("SOME_PUNCT")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"IS_PUNCT": True}],
            "label": "SOME_PUNCT"
        }

    def test_number(self):
        rules = self.compiler('NUM("42")->MARK("SOME_NUMBER")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"LOWER": "42"}],
            "label": "SOME_NUMBER"
        }

    def test_pos(self):
        rules = self.compiler('POS("VERB")->MARK("SOME_POS")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"POS": "VERB"}],
            "label": "SOME_POS"
        }

    def test_single_word(self):
        rules = self.compiler('WORD("Test")->MARK("SOME_LABEL")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"LOWER": "test"}],
            "label": "SOME_LABEL"
        }

    def test_multiple_words(self):
        rules = self.compiler('''
        words = {"test1", "test2"}
        IN_LIST(words)->MARK("MULTI_LABEL")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"LOWER": {"REGEX": "^(test1|test2)$"}}],
            "label": "MULTI_LABEL"
        }

    def test_simple_pattern(self):
        rules = self.compiler('''
        {WORD("test1"), WORD("test2")}->MARK("SIMPLE_PATTERN")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "pattern": [{"LOWER": "test1"}, self.punct, {"LOWER": "test2"}],
            "label": "SIMPLE_PATTERN"
        }

    def test_or_branch(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2")}->MARK("SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == {
            "pattern": [{"LOWER": "test1"}],
            "label": "SPLIT_LABEL"
        }
        assert rules[1] == {
            "pattern": [{"LOWER": "test2"}],
            "label": "SPLIT_LABEL"
        }

    def test_or_branch_multi(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2"),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == {
            "pattern": [{"LOWER": "test1"}, self.punct, {"LOWER": "test3"}],
            "label": "MULTI_SPLIT_LABEL"
        }
        assert rules[1] == {
            "pattern": [{"LOWER": "test2"}, self.punct, {"LOWER": "test3"}],
            "label": "MULTI_SPLIT_LABEL"
        }
        assert rules[2] == {
            "pattern": [{"LOWER": "test1"}, self.punct, {"LOWER": "test4"}],
            "label": "MULTI_SPLIT_LABEL"
        }
        assert rules[3] == {
            "pattern": [{"LOWER": "test2"}, self.punct, {"LOWER": "test4"}],
            "label": "MULTI_SPLIT_LABEL"
        }

    def test_or_branch_multi_w_single(self):
        rules = self.compiler('''
        numbers={"one", "two", "three"}
        {WORD("test1")|WORD("test2"),IN_LIST(numbers),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        list_items = {"LOWER": {"REGEX": "^(one|three|two)$"}}
        assert rules[0] == {
            "pattern": [{"LOWER": "test1"}, self.punct, list_items, self.punct, {"LOWER": "test3"}],
            "label": "MULTI_SPLIT_LABEL"
        }
        assert rules[1] == {
            "pattern": [{"LOWER": "test2"}, self.punct, list_items, self.punct, {"LOWER": "test3"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[2] == {
            "pattern": [{"LOWER": "test1"}, self.punct, list_items, self.punct, {"LOWER": "test4"}],
            "label": "MULTI_SPLIT_LABEL"
        }
        assert rules[3] == {
            "pattern": [{"LOWER": "test2"}, self.punct, list_items, self.punct, {"LOWER": "test4"}],
            "label": "MULTI_SPLIT_LABEL"
        }

    def test_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == {
            "label": "SPLIT_LIST",
            "pattern": [{"LOWER": {"REGEX": "^(test1|test2|test4)$"}}]
        }
        assert rules[1] == {
            "label": "SPLIT_LIST",
            "pattern": [{"LOWER": "test"}, {"LOWER": "-"}, {"LOWER": "3"}]
        }

    def test_double_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4", "test-5"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 3
        assert rules[0] == {
            "label": "SPLIT_LIST",
            "pattern": [{"LOWER": {"REGEX": "^(test1|test2|test4)$"}}]
        }
        assert rules[1] == {
            "label": "SPLIT_LIST",
            "pattern": [{"LOWER": "test"}, {"LOWER": "-"}, {"LOWER": "3"}]
        }
        assert rules[2] == {
            "label": "SPLIT_LIST",
            "pattern": [{"LOWER": "test"}, {"LOWER": "-"}, {"LOWER": "5"}]
        }

    def test_word_with_spaces(self):
        rules = self.compiler('''
        WORD("test1 test2")->MARK("SPLIT_WORD")
        ''')
        print(rules)
        # It should be split into two: WORD("test1"), WORD("test2")
        assert len(rules) == 1
        assert rules[0] == {
            "label": "SPLIT_WORD",
            "pattern": [{"LOWER": "test1"}, {"LOWER": "test2"}]
        }

    def test_word_with_dash(self):
        rules = self.compiler('''
        WORD("test1-test2")->MARK("SPLIT_WORD")
        ''')
        print(rules)
        # It should be split into two: WORD("test1"), WORD("test2")
        assert len(rules) == 1
        assert rules[0] == {
            "label": "SPLIT_WORD",
            "pattern": [{"LOWER": "test1"}, {"LOWER": "-"}, {"LOWER": "test2"}]
        }

    def test_word_with_accent(self):
        rules = self.compiler('''
        WORD("Šarūnas")->MARK("TWO_WORDS")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "TWO_WORDS",
            "pattern": [{"LOWER": {"REGEX": "^(sarunas|šarūnas)$"}}]
        }

    def test_list_with_accent(self):
        rules = self.compiler('''
        names={"Jonas", "Jurgis", "Šarūnas"}
        IN_LIST(names)->MARK("EXTENDED_LIST")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "EXTENDED_LIST",
            "pattern": [{"LOWER": {"REGEX": "^(jonas|jurgis|sarunas|šarūnas)$"}}]
        }

    def test_prefix_on_word(self):
        rules = self.compiler('''
        {PREFIX("meta"), WORD("physics")}->MARK("META_WORD")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "META_WORD",
            "pattern": [{"LOWER": "metaphysics"}]
        }

    def test_prefix_on_list(self):
        rules = self.compiler('''
        science = {"physics", "mathematics"}
        {PREFIX("meta"), IN_LIST(science)}->MARK("META_LIST")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "META_LIST",
            "pattern": [{"LOWER": {"REGEX": "^(metamathematics|metaphysics)$"}}]
        }

    def test_prefix_on_unknown_type(self):
        rules = self.compiler('''
        {PREFIX("test"), ANY}->MARK("NOT_VALID")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "NOT_VALID",
            "pattern": [{"LOWER": {"REGEX": ".*"}}]
        }

    def test_multiple_optionals(self):
        rules = self.compiler("""
        {NUM+, WORD("-")?, NUM?, WORD("/")?, NUM?}->MARK("NUMBER_PATTERN")
        """)
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {
            "label": "NUMBER_PATTERN",
            "pattern": [
                {"LOWER": {"REGEX": "\\d+[.]?\\d*"}, "OP": "+"},
                {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": "-", "OP": "?"},
                {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": {"REGEX": "\\d+[.]?\\d*"}, "OP": "?"},
                {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": "/", "OP": "?"},
                {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": {"REGEX": "\\d+[.]?\\d*"}, "OP": "?"},
            ]
        }

    def test_optional_list(self):
        rules = self.compiler("""
        elements = {"one", "two"}
        {IN_LIST(elements)?}->MARK("OPTIONAL_LIST")
        """)

        print(rules)

        assert len(rules) == 1
        assert rules[0] == {
            "label": "OPTIONAL_LIST",
            "pattern": [{"LOWER": {"REGEX": "^(one|two)$", "OP": "?"}}]
        }


class TestStandalone(object):
    @property
    def punct(self):
        return re.compile(r"[.,!;?:]")

    @property
    def flags(self):
        return re.DOTALL | re.IGNORECASE

    def compiler(self, rules):
        return rita.compile_string(rules, use_engine="standalone").patterns

    def test_punct(self):
        rules = self.compiler('PUNCT->MARK("SOME_PUNCT")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SOME_PUNCT>([.,!;?:]\s?))", self.flags)

    def test_number(self):
        rules = self.compiler('NUM("42")->MARK("SOME_NUMBER")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SOME_NUMBER>(42\s?))", self.flags)

    def test_single_word(self):
        rules = self.compiler('WORD("Test")->MARK("SOME_LABEL")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SOME_LABEL>(Test\s?))", self.flags)

    def test_multiple_words(self):
        rules = self.compiler('''
        words = {"test1", "test2"}
        IN_LIST(words)->MARK("MULTI_LABEL")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<MULTI_LABEL>(^|\s)((test1|test2)\s?))", self.flags)

    def test_simple_pattern(self):
        rules = self.compiler('''
        {WORD("test1"), WORD("test2")}->MARK("SIMPLE_PATTERN")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SIMPLE_PATTERN>(test1\s?)([.,!;?:]\s?)?(test2\s?))", self.flags)

    def test_or_branch(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2")}->MARK("SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == re.compile(r"(?P<SPLIT_LABEL>(test1\s?))", self.flags)
        assert rules[1] == re.compile(r"(?P<SPLIT_LABEL>(test2\s?))", self.flags)

    def test_or_branch_multi(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2"),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1\s?)([.,!;?:]\s?)?(test3\s?))", self.flags)
        assert rules[1] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2\s?)([.,!;?:]\s?)?(test3\s?))", self.flags)
        assert rules[2] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1\s?)([.,!;?:]\s?)?(test4\s?))", self.flags)
        assert rules[3] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2\s?)([.,!;?:]\s?)?(test4\s?))", self.flags)

    def test_or_branch_multi_w_single(self):
        rules = self.compiler('''
        numbers={"one", "two", "three"}
        {WORD("test1")|WORD("test2"),IN_LIST(numbers),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == re.compile(
            r"(?P<MULTI_SPLIT_LABEL>(test1\s?)([.,!;?:]\s?)?(^|\s)((three|one|two)\s?)([.,!;?:]\s?)?(test3\s?))",
            self.flags
        )
        assert rules[1] == re.compile(
            r"(?P<MULTI_SPLIT_LABEL>(test2\s?)([.,!;?:]\s?)?(^|\s)((three|one|two)\s?)([.,!;?:]\s?)?(test3\s?))",
            self.flags
        )
        assert rules[2] == re.compile(
            r"(?P<MULTI_SPLIT_LABEL>(test1\s?)([.,!;?:]\s?)?(^|\s)((three|one|two)\s?)([.,!;?:]\s?)?(test4\s?))",
            self.flags
        )
        assert rules[3] == re.compile(
            r"(?P<MULTI_SPLIT_LABEL>(test2\s?)([.,!;?:]\s?)?(^|\s)((three|one|two)\s?)([.,!;?:]\s?)?(test4\s?))",
            self.flags
        )

    def test_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == re.compile(r"(?P<SPLIT_LIST>(^|\s)((test1|test2|test4)\s?))", self.flags)
        assert rules[1] == re.compile(r"(?P<SPLIT_LIST>(test-3\s?))", self.flags)

    def test_word_with_accent(self):
        rules = self.compiler('''
        WORD("Šarūnas")->MARK("TWO_WORDS")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<TWO_WORDS>(^|\s)((Sarunas|Šarūnas)\s?))", self.flags)

    def test_list_with_accent(self):
        rules = self.compiler('''
        names={"Jonas", "Jurgis", "Šarūnas"}
        IN_LIST(names)->MARK("EXTENDED_LIST")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<EXTENDED_LIST>(^|\s)((Sarunas|Šarūnas|Jurgis|Jonas)\s?))", self.flags)

    def test_double_op(self):
        rules = self.compiler('''
        WORD+->MARK("DOUBLE_OP")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<DOUBLE_OP>((\w|['_-])+\s?)+)", self.flags)

    def test_prefix_on_word(self):
        rules = self.compiler('''
        {PREFIX("meta"), WORD("physics")}->MARK("META_WORD")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<META_WORD>(metaphysics\s?))", self.flags)

    def test_prefix_on_list(self):
        rules = self.compiler('''
        science = {"physics", "mathematics"}
        {PREFIX("meta"), IN_LIST(science)}->MARK("META_LIST")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<META_LIST>(^|\s)((metamathematics|metaphysics)\s?))", self.flags)

    def test_prefix_on_unknown_type(self):
        rules = self.compiler('''
        {PREFIX("test"), ANY}->MARK("NOT_VALID")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<NOT_VALID>(.*\s?))", self.flags)

    def test_save_and_load_rules_from_file(self):
        rules = '''
        {WORD("Hello"), WORD("world")}->MARK("HELLO")
        '''
        engine = rita.compile_string(rules, use_engine="standalone")
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_path = os.path.join(tmpdir, "rules-example.json")
            engine.save(rules_path)
            engine.load(rules_path)
            engine.execute("Hello world")
