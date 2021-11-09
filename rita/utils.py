import logging

from contextlib import contextmanager
from unicodedata import normalize, category
from itertools import cycle, chain
from time import time
from json import JSONEncoder

logger = logging.getLogger(__name__)


class Node(object):
    """
    An utility structure. Has no meaning outside
    Allows to specify single path showing how it branches
    and by doing `unwrap` we get multiple lists for each possible variation
    """
    def __init__(self, data=None):
        self.data = data
        self.children = []
        self.next_node = None
        self.children_cycle = None
        self.ref_count = 0
        self.depth = 0
        self.current = None

    def add_child(self, c):
        self.children.append(Node(c))
        self.reset_cycle()

    def add_next(self, node):
        self.next_node = node

    @property
    def child(self):
        # Corner case of 0 depth
        if self.depth == 0:
            result = self.current
            self.next_child()
            return result

        if self.ref_count >= self.depth:
            self.next_child()
            self.ref_count = 0
        else:
            self.ref_count += 1
        return self.current

    def next_child(self):
        self.current = next(self.children_cycle)

    def reset_cycle(self):
        self.children_cycle = cycle(self.children)
        self.current = next(self.children_cycle)

    def unwrap(self):
        variants = 1
        current = self
        while current is not None:
            variants *= current.weight
            current = current.next_node

        logger.debug("Total variants: {}".format(variants))

        for i in range(0, variants):
            result = []
            current = self
            while current is not None:
                if current.data:
                    result.append(current.data)
                if len(current.children) > 0:
                    c = current.child
                    result.append(c.data)
                current = current.next_node
            yield result

    @property
    def weight(self):
        if len(self.children) == 0:
            return 1
        else:
            return len(self.children)

    def __repr__(self):
        return "{data}[{children}] -> {next_node}".format(
            data=self.data,
            children=", ".join(map(str, self.children)),
            next_node=str(self.next_node)
        )


class SingletonMixin(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


def deaccent(text):
    return normalize("NFC",
                     "".join(c
                             for c in normalize("NFD", text)
                             if category(c) != "Mn"))


def flatten(lst, shallow=False):
    def explode(v):
        if callable(v):
            return v()
        else:
            return v

    if len(lst) > 1 and not shallow:
        return lst

    new_lst = map(explode, lst)
    if shallow:
        return new_lst
    else:
        return chain(*new_lst)


class ExtendedOp(object):
    def __init__(self, op=None):
        self.case_sensitive_override = False
        self.local_regex_override = False
        if isinstance(op, ExtendedOp):
            self.op = op.op
            self.case_sensitive_override = op.case_sensitive_override
            self.local_regex_override = op.local_regex_override
        else:
            self.op = op

    @property
    def value(self):
        return self.op

    def empty(self):
        return self.op is None or self.op.strip() == ""

    def ignore_case(self, config):
        if self.case_sensitive_override:
            return False
        else:
            return config.ignore_case

    def __str__(self):
        if self.op:
            return self.op
        return ""

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if type(other) == str:
            return self.op == other

        return (
            self.op == other.op and
            self.case_sensitive_override == other.case_sensitive_override and
            self.local_regex_override == other.local_regex_override
        )


class Timer(object):
    def __init__(self, title):
        self.title = title
        self.ts = time()

    def stop(self, debug=True):
        now = time()
        delta = int(now - self.ts) * 1000
        msg = "{} took {}ms".format(self.title, delta)
        if debug:
            logger.debug(msg)
        else:
            logger.info(msg)
        return delta


@contextmanager
def timer(title):
    t = Timer(title)
    yield
    t.stop()


class RitaJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ExtendedOp):
            return o.op
        return o.__dict__
