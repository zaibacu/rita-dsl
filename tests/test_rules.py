import re

import pytest
import rita

from utils import spacy_engine, standalone_engine


class TestSpacy(object):
    @property
    def punct(self):
        return {'IS_PUNCT': True, 'OP': '?'}
    
    def compiler(self, rules):
        spacy = pytest.importorskip("spacy", minversion="2.1")
        return rita.compile_string(rules, use_engine="spacy")
        
    def test_single_word(self):
        rules = self.compiler('WORD("Test")->MARK("SOME_LABEL")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {"pattern": [{"ORTH": "Test"}], "label": "SOME_LABEL"}

    def test_multiple_words(self):
        rules = self.compiler('''
        words = {"test1", "test2"}
        IN_LIST(words)->MARK("MULTI_LABEL")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {"pattern": [{"LOWER": {"REGEX": "(test1|test2)"}}], "label": "MULTI_LABEL"}

    def test_simple_pattern(self):
        rules = self.compiler('''
        {WORD("test1"), WORD("test2")}->MARK("SIMPLE_PATTERN")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == {"pattern": [{"ORTH": "test1"}, self.punct, {"ORTH": "test2"}], "label": "SIMPLE_PATTERN"}
        

    def test_or_branch(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2")}->MARK("SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == {"pattern": [{"ORTH": "test1"}], "label": "SPLIT_LABEL"}
        assert rules[1] == {"pattern": [{"ORTH": "test2"}], "label": "SPLIT_LABEL"}

    def test_or_branch_multi(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2"),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == {"pattern": [{"ORTH": "test1"}, self.punct, {"ORTH": "test3"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[1] == {"pattern": [{"ORTH": "test2"}, self.punct, {"ORTH": "test3"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[2] == {"pattern": [{"ORTH": "test1"}, self.punct, {"ORTH": "test4"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[3] == {"pattern": [{"ORTH": "test2"}, self.punct, {"ORTH": "test4"}], "label": "MULTI_SPLIT_LABEL"}

    def test_or_branch_multi_w_single(self):
        rules = self.compiler('''
        numbers={"one", "two", "three"}
        {WORD("test1")|WORD("test2"),IN_LIST(numbers),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        list_items = {"LOWER": {"REGEX": "(one|three|two)"}}
        assert rules[0] == {"pattern": [{"ORTH": "test1"}, self.punct, list_items, self.punct, {"ORTH": "test3"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[1] == {"pattern": [{"ORTH": "test2"}, self.punct, list_items, self.punct, {"ORTH": "test3"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[2] == {"pattern": [{"ORTH": "test1"}, self.punct, list_items, self.punct, {"ORTH": "test4"}], "label": "MULTI_SPLIT_LABEL"}
        assert rules[3] == {"pattern": [{"ORTH": "test2"}, self.punct, list_items, self.punct, {"ORTH": "test4"}], "label": "MULTI_SPLIT_LABEL"}

    def test_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == {"label": "SPLIT_LIST", "pattern": [{"LOWER": {"REGEX": "(test1|test2|test4)"}}]}
        assert rules[1] == {"label": "SPLIT_LIST", "pattern": [{"ORTH": "test"}, {"ORTH": "-"}, {"ORTH": "3"}]}

    def test_double_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4", "test-5"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 3
        assert rules[0] == {"label": "SPLIT_LIST", "pattern": [{"LOWER": {"REGEX": "(test1|test2|test4)"}}]}
        assert rules[1] == {"label": "SPLIT_LIST", "pattern": [{"ORTH": "test"}, {"ORTH": "-"}, {"ORTH": "3"}]}
        assert rules[2] == {"label": "SPLIT_LIST", "pattern": [{"ORTH": "test"}, {"ORTH": "-"}, {"ORTH": "5"}]}
        

class TestStandalone(object):
    @property
    def punct(self):
        return re.compile(r"[.,!;?:]")

    def compiler(self, rules):
        return rita.compile_string(rules, use_engine="standalone").patterns
    
    def test_single_word(self):
        rules = self.compiler('WORD("Test")->MARK("SOME_LABEL")')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SOME_LABEL>(Test))", re.IGNORECASE)

    def test_multiple_words(self):
        rules = self.compiler('''
        words = {"test1", "test2"}
        IN_LIST(words)->MARK("MULTI_LABEL")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<MULTI_LABEL>(test1|test2))", re.IGNORECASE)

    def test_simple_pattern(self):
        rules = self.compiler('''
        {WORD("test1"), WORD("test2")}->MARK("SIMPLE_PATTERN")
        ''')
        print(rules)
        assert len(rules) == 1
        assert rules[0] == re.compile(r"(?P<SIMPLE_PATTERN>(test1)[.,!;?:]?\s(test2))", re.IGNORECASE)

    def test_or_branch(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2")}->MARK("SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == re.compile(r"(?P<SPLIT_LABEL>(test1))", re.IGNORECASE)
        assert rules[1] == re.compile(r"(?P<SPLIT_LABEL>(test2))", re.IGNORECASE)

    def test_or_branch_multi(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2"),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1)[.,!;?:]?\s(test3))", re.IGNORECASE)
        assert rules[1] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2)[.,!;?:]?\s(test3))", re.IGNORECASE)
        assert rules[2] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1)[.,!;?:]?\s(test4))", re.IGNORECASE)
        assert rules[3] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2)[.,!;?:]?\s(test4))", re.IGNORECASE)

    def test_or_branch_multi_w_single(self):
        rules = self.compiler('''
        numbers={"one", "two", "three"}
        {WORD("test1")|WORD("test2"),IN_LIST(numbers),WORD("test3")|WORD("test4")}->MARK("MULTI_SPLIT_LABEL")
        ''')
        print(rules)
        assert len(rules) == 4
        assert rules[0] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1)[.,!;?:]?\s(one|three|two)[.,!;?:]?\s(test3))", re.IGNORECASE)
        assert rules[1] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2)[.,!;?:]?\s(one|three|two)[.,!;?:]?\s(test3))", re.IGNORECASE)
        assert rules[2] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test1)[.,!;?:]?\s(one|three|two)[.,!;?:]?\s(test4))", re.IGNORECASE)
        assert rules[3] == re.compile(r"(?P<MULTI_SPLIT_LABEL>(test2)[.,!;?:]?\s(one|three|two)[.,!;?:]?\s(test4))", re.IGNORECASE)

    def test_branching_list(self):
        rules = self.compiler('''
        items={"test1", "test2", "test-3", "test4"}
        {IN_LIST(items)}->MARK("SPLIT_LIST")
        ''')
        print(rules)
        assert len(rules) == 2
        assert rules[0] == re.compile(r"(?P<SPLIT_LIST>(test1|test2|test4))", re.IGNORECASE)
        assert rules[1] == re.compile(r"(?P<SPLIT_LIST>(test-3))", re.IGNORECASE)

