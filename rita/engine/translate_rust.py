import os
import logging

from ctypes import (c_char_p, c_size_t, c_uint, Structure, cdll, POINTER)

from rita.engine.translate_standalone import rules_to_patterns, RuleExecutor

logger = logging.getLogger(__name__)


class ResultEntity(Structure):
    _fields_ = [
        ("label", c_char_p),
        ("start", c_size_t),
        ("end", c_size_t),
    ]


class ResultsWrapper(Structure):
    _fields_ = [
        ("count", c_uint),
        ("results", (ResultEntity * 32))
    ]


class Context(Structure):
    _fields_ = []


def load_lib():
    try:
        if "nt" in os.name:
            lib = cdll.LoadLibrary("rita_rust.dll")
        elif os.name == "posix":
            lib = cdll.LoadLibrary("librita_rust.dylib")
        else:
            lib = cdll.LoadLibrary("librita_rust.so")
        lib.compile.restype = POINTER(Context)
        lib.execute.argtypes = [POINTER(Context), c_char_p]
        lib.execute.restype = ResultsWrapper
        lib.clean_env.argtypes = [POINTER(Context)]
        return lib
    except Exception as ex:
        logger.error("Failed to load rita-rust library, reason: {}\n\n"
                     "Most likely you don't have required shared library to use it".format(ex))


class RustRuleExecutor(RuleExecutor):
    def __init__(self, patterns, config):
        self.config = config
        self.context = None

        self.lib = load_lib()
        self.patterns = [self._build_regex_str(label, rules)
                         for label, rules in patterns]

        self.compile()

    @staticmethod
    def _build_regex_str(label, rules):
        return r"(?P<{0}>{1})".format(label, "".join(rules))

    def compile(self):
        flag = 0 if self.config.ignore_case else 1
        c_array = (c_char_p * len(self.patterns))(*list([p.encode("UTF-8") for p in self.patterns]))
        self.context = self.lib.compile(c_array, len(c_array), flag)
        return self.context

    def execute(self, text):
        raw = self.lib.execute(self.context, text.encode("UTF-8"))
        for i in range(0, raw.count):
            match = raw.results[i]
            matched_text = text[match.start:match.end].strip()
            yield {
                "start": match.start,
                "end": match.end,
                "text": matched_text,
                "label": match.label.decode("UTF-8"),
            }

    def clean_context(self):
        self.lib.clean_env(self.context)


def compile_rules(rules, config, **kwargs):
    logger.info("Using rita-rust rule implementation")
    patterns = [rules_to_patterns(*group) for group in rules]
    executor = RustRuleExecutor(patterns, config)
    return executor
