from functools import lru_cache

from tinyoscquery.shared.osc_path_node import OSCPathNode


class OSCNamespace:
    def __init__(self):
        self._root = OSCPathNode("/", description="root node")

    @property
    def root_node(self) -> OSCPathNode:
        return self._root

    @property
    @lru_cache()
    def number_of_nodes(self) -> int:
        number_of_nodes = 0
        for _ in self._root:
            number_of_nodes += 1
        return number_of_nodes

    def add_node(self, node: OSCPathNode):
        self._root.add_child_node(node)
        self.__class__.number_of_nodes.fget.cache_clear()

    def __repr__(self) -> str:
        return f"OSCNamespace({self.number_of_nodes} nodes)"
