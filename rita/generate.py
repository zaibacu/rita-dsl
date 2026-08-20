"""
Rule generator: build a minimal rita ruleset from annotated examples.

Input is a CSV file where each row holds:
  1. raw text
  2. the span inside that text which should be marked
  3. the label to mark it with

The generator tokenizes every span, groups spans by label and token shape,
and merges them into as few rules as possible:

- same token shape -> one rule; positions with several observed values
  become an ``IN_LIST``, number positions with several values become
  a generic ``NUM``
- a shape which equals another shape with exactly one token removed is
  folded into it, the extra token becoming optional (``?``)

The generated ruleset is validated with the standalone engine against
every input row, so full coverage is checked, not assumed.
"""
import argparse
import csv
import logging
import re
import sys

from collections import OrderedDict
from typing import Dict, List, NamedTuple, Optional, Tuple

logger = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"\d+[.,]\d+|\d+|\w+(?:[-']\w+)*|\S", re.UNICODE)
NUM_RE = re.compile(r"^(\d+[.,]\d+|\d+)$")
PUNCT_CHARS = set(".,!;?:")
VALID_LABEL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Token(NamedTuple):
    kind: str  # "word" | "num" | "punct"
    value: str


class Slot:
    """One token position of a generated rule"""

    def __init__(self, kind: str, optional: bool = False):
        self.kind = kind
        self.values: "OrderedDict[str, None]" = OrderedDict()
        self.optional = optional

    def add(self, value: str) -> None:
        # Case-insensitive dedup, keep first-seen casing
        for existing in self.values:
            if existing.lower() == value.lower():
                return
        self.values[value] = None

    def merge(self, other: "Slot") -> None:
        for v in other.values:
            self.add(v)
        self.optional = self.optional or other.optional


class Rule:
    def __init__(self, label: str, tokens: List[Token]):
        self.label = label
        self.slots = [Slot(t.kind) for t in tokens]
        for slot, token in zip(self.slots, tokens):
            slot.add(token.value)

    @property
    def signature(self) -> Tuple[str, ...]:
        return tuple(s.kind for s in self.slots)

    def absorb(self, tokens: List[Token]) -> None:
        for slot, token in zip(self.slots, tokens):
            slot.add(token.value)


class RowError(NamedTuple):
    line: int
    reason: str


def tokenize(span: str) -> List[Token]:
    tokens = []
    for value in TOKEN_RE.findall(span):
        if NUM_RE.match(value):
            tokens.append(Token("num", value))
        elif value in PUNCT_CHARS:
            tokens.append(Token("punct", value))
        else:
            tokens.append(Token("word", value))
    return tokens


def read_rows(path: str, delimiter: str = ","):
    """
    Yield (line_number, text, span, label) for every data row.
    A first row spelling out text/span/label is treated as a header.
    """
    with open(path, "r", encoding="UTF-8", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for line, row in enumerate(reader, 1):
            if len(row) == 0 or all(not cell.strip() for cell in row):
                continue
            if line == 1 and [c.strip().lower() for c in row[:3]] == ["text", "span", "label"]:
                continue
            yield line, row


def collect_rules(rows, errors: List[RowError]) -> List[Rule]:
    rules: List[Rule] = []
    by_key: Dict[Tuple[str, Tuple[str, ...]], Rule] = {}

    for line, row in rows:
        if len(row) < 3:
            errors.append(RowError(line, "expected 3 columns (text, span, label), got {}".format(len(row))))
            continue
        text, span, label = row[0], row[1].strip(), row[2].strip()
        if not span:
            errors.append(RowError(line, "empty span"))
            continue
        if not VALID_LABEL.match(label):
            errors.append(RowError(line, "invalid label '{}' - use letters, digits and underscores".format(label)))
            continue
        if span.lower() not in text.lower():
            errors.append(RowError(line, "span '{}' does not occur in the text".format(span)))
            continue

        tokens = tokenize(span)
        if len(tokens) == 0:
            errors.append(RowError(line, "span '{}' has no tokens".format(span)))
            continue

        key = (label, tuple(t.kind for t in tokens))
        if key in by_key:
            by_key[key].absorb(tokens)
        else:
            rule = Rule(label, tokens)
            by_key[key] = rule
            rules.append(rule)

    return rules


def _merge_with_deletion(target: Rule, source: Rule) -> bool:
    """
    If `source`'s signature equals `target`'s with exactly one slot deleted,
    fold `source` into `target`, making the extra slot optional
    """
    a, b = target.signature, source.signature
    if len(a) != len(b) + 1:
        return False
    for skip in range(len(a)):
        if a[:skip] + a[skip + 1:] == b:
            target.slots[skip].optional = True
            for i, slot in enumerate(source.slots):
                target.slots[i if i < skip else i + 1].merge(slot)
            return True
    return False


def minimize_rules(rules: List[Rule]) -> List[Rule]:
    """
    Fold rules whose shape differs by a single extra token
    into one rule with an optional slot
    """
    result: List[Rule] = []
    for rule in sorted(rules, key=lambda r: -len(r.slots)):
        merged = False
        for existing in result:
            if existing.label != rule.label:
                continue
            if existing.signature == rule.signature:
                for mine, theirs in zip(existing.slots, rule.slots):
                    mine.merge(theirs)
                merged = True
                break
            if _merge_with_deletion(existing, rule):
                merged = True
                break
        if not merged:
            result.append(rule)
    return result


def escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class Renderer:
    def __init__(self):
        self.variables: "OrderedDict[str, List[str]]" = OrderedDict()

    def _variable_for(self, label: str, values: List[str]) -> str:
        for name, existing in self.variables.items():
            if [v.lower() for v in existing] == [v.lower() for v in values]:
                return name
        name = "{}_list_{}".format(label.lower(), len(self.variables))
        self.variables[name] = values
        return name

    def render_slot(self, label: str, slot: Slot) -> str:
        suffix = "?" if slot.optional else ""
        values = list(slot.values)
        if slot.kind == "punct":
            return "PUNCT" + suffix
        if slot.kind == "num":
            if len(values) == 1:
                return 'NUM("{}"){}'.format(escape(values[0]), suffix)
            return "NUM" + suffix
        if len(values) == 1:
            return 'WORD("{}"){}'.format(escape(values[0]), suffix)
        name = self._variable_for(label, values)
        return "IN_LIST({}){}".format(name, suffix)

    def render(self, rules: List[Rule]) -> str:
        bodies = []
        for rule in rules:
            slots = ", ".join(self.render_slot(rule.label, s) for s in rule.slots)
            bodies.append('{{{0}}}->MARK("{1}")'.format(slots, rule.label))

        lines = []
        for name, values in self.variables.items():
            items = ", ".join('"{}"'.format(escape(v)) for v in values)
            lines.append("{} = {{{}}}".format(name, items))
        if lines:
            lines.append("")
        lines.extend(bodies)
        return "\n".join(lines) + "\n"


def validate(rules_source: str, rows, errors: List[RowError]) -> List[RowError]:
    """
    Compile the generated ruleset with the standalone engine and check
    that every input row's span is found with the right label
    """
    import rita

    misses: List[RowError] = []
    parser = rita.compile_string(rules_source, use_engine="standalone")
    failed_lines = {e.line for e in errors}
    for line, row in rows:
        if line in failed_lines or len(row) < 3:
            continue
        text, span, label = row[0], row[1].strip(), row[2].strip()
        results = list(parser.execute(text))
        if not any(r["label"] == label and r["text"].lower() == span.lower()
                   for r in results):
            found = ["{}:{}".format(r["label"], r["text"]) for r in results]
            misses.append(RowError(
                line, "'{}' ({}) not covered; engine found: {}".format(span, label, found or "nothing")))
    return misses


def generate(path: str, delimiter: str = ",", do_validate: bool = True):
    errors: List[RowError] = []
    rows = list(read_rows(path, delimiter=delimiter))
    rules = minimize_rules(collect_rules(rows, errors))
    if len(rules) == 0:
        return None, errors, [RowError(0, "no rules could be generated")]
    source = Renderer().render(rules)
    misses = validate(source, rows, errors) if do_validate else []
    return source, errors, misses


def main(argv: Optional[List[str]] = None) -> int:
    arg_parser = argparse.ArgumentParser(
        description="Generate a minimal rita ruleset from a CSV of (text, span, label) examples"
    )
    arg_parser.add_argument("-f", required=True, help="input .csv file: text, span, label")
    arg_parser.add_argument("-o", help="output .rita file (default: stdout)")
    arg_parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    arg_parser.add_argument("--no-validate", action="store_true",
                            help="skip validating the generated rules against the input")
    arg_parser.add_argument("--debug", action="store_true", help="debug mode")
    args = arg_parser.parse_args(argv)

    # WARNING by default - the rita compiler used for validation is
    # noisy at INFO level and the ruleset goes to stdout
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    source, errors, misses = generate(args.f, delimiter=args.delimiter,
                                      do_validate=not args.no_validate)

    for err in errors:
        print("Row {} skipped: {}".format(err.line, err.reason), file=sys.stderr)
    for miss in misses:
        print("Row {} NOT covered: {}".format(miss.line, miss.reason), file=sys.stderr)

    if source is None:
        print("No rules generated", file=sys.stderr)
        return 1

    if args.o:
        with open(args.o, "w", encoding="UTF-8") as f:
            f.write(source)
        print("Wrote {}".format(args.o), file=sys.stderr)
    else:
        sys.stdout.write(source)

    n_rules = sum(1 for line in source.splitlines() if "->MARK(" in line)
    status = "coverage OK" if not (errors or misses) else \
        "{} skipped, {} not covered".format(len(errors), len(misses))
    print("Generated {} rules ({})".format(n_rules, status), file=sys.stderr)

    if misses or errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
