import logging

logger = logging.getLogger(__name__)


class Node(object):
    def __init__(self, data=None):
        self.data = data
        self.children = []
        self.next_node = None

    def add_child(self, c):
        self.children.append(Node(c))

    def add_next(self, node):
        self.next_node = node

    def unwrap(self):
        variants = 1
        current = self
        while current != None:
            variants *= current.weight
            current = current.next_node

        logger.debug("Total variants: {}".format(variants))
        if variants > 256:
            raise RuntimeError("Sorry, branching went a bit too far. Check your syntax")
        
        for i in range(0, variants):
            mask = map(int, list("{0:08b}".format(i)[::-1]))
            result = []
            current = self
            while current != None:
                if current.data:
                    result.append(current.data)
                if len(current.children) > 0:
                    m = next(mask)
                    result.append(current.children[m].data)
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
