import logging

from unicodedata import normalize, category
from itertools import cycle, chain

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
