import re

import pytest
import rita

from utils import spacy_engine, standalone_engine


class TestSpacy(object):
    def compiler(self, rules):
        spacy = pytest.importorskip("spacy", minversion="2.1")
        from rita.engine.translate_spacy import compile_rules
        return rita.compile_string(rules, compile_fn=compile_rules)
        
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

    def test_or_branch(self):
        rules = self.compiler('''
        {WORD("test1")|WORD("test2")}->MARK("SINGLE_LABEL")
        ''')
        print(rules)
        assert len(rules) == 2
        

class TestStandalone(object):
    def compiler(self, rules):
        from rita.engine.translate_standalone import compile_rules
        return rita.compile_string(rules, compile_fn=compile_rules).patterns
    
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

