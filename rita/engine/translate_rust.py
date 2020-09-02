import os
import logging

from ctypes import (c_char_p, c_int, c_uint, c_long, Structure, cdll, POINTER)

from rita.engine.translate_standalone import rules_to_patterns, RuleExecutor

logger = logging.getLogger(__name__)


class NamedRangeResult(Structure):
    _fields_ = [
        ("start", c_long),
        ("end", c_long),
        ("name", c_char_p),
    ]


class ResultEntity(Structure):
    _fields_ = [
        ("label", c_char_p),
        ("start", c_long),
        ("end", c_long),
        ("sub_count", c_uint),
    ]


class Result(Structure):
    _fields_ = [
        ("count", c_uint)
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
        lib.execute.restype = POINTER(Result)
        lib.clean_env.argtypes = [POINTER(Context)]
        lib.clean_result.argtypes = [POINTER(Result)]
        lib.read_result.argtypes = [POINTER(Result), c_int]
        lib.read_result.restype = POINTER(ResultEntity)
        lib.read_submatch.argtypes = [POINTER(ResultEntity), c_int]
        lib.read_submatch.restype = POINTER(NamedRangeResult)
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
        indexed_rules = ["(?P<s{}>{})".format(i, r) if not r.startswith("(?P<") else r
                         for i, r in enumerate(rules)]
        return r"(?P<{0}>{1})".format(label, "".join(indexed_rules))

    def compile(self):
        flag = 0 if self.config.ignore_case else 1
        c_array = (c_char_p * len(self.patterns))(*list([p.encode("UTF-8") for p in self.patterns]))
        self.context = self.lib.compile(c_array, len(c_array), flag)
        return self.context

    def execute(self, text, include_submatches=True):
        result_ptr = self.lib.execute(self.context, text.encode("UTF-8"))
        count = result_ptr[0].count
        for i in range(0, count):
            match_ptr = self.lib.read_result(result_ptr, i)
            match = match_ptr[0]
            matched_text = text[match.start:match.end].strip()

            def parse_subs():
                k = match.sub_count
                for j in range(0, k):
                    s = self.lib.read_submatch(match_ptr, j)[0]
                    start = s.start
                    end = s.end
                    sub_text = text[start:end]

                    if sub_text.strip() == "":
                        continue

                    yield {
                        "text": sub_text.strip(),
                        "start": start,
                        "end": end,
                        "key": s.name.decode("UTF-8"),
                    }

            yield {
                "start": match.start,
                "end": match.end,
                "text": matched_text,
                "label": match.label.decode("UTF-8"),
                "submatches": list(parse_subs()) if include_submatches else []
            }

    def clean_context(self):
        self.lib.clean_env(self.context)


def compile_rules(rules, config, **kwargs):
    logger.info("Using rita-rust rule implementation")
    patterns = [rules_to_patterns(*group, config=config) for group in rules]
    executor = RustRuleExecutor(patterns, config)
    return executor
