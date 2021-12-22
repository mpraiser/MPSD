from __future__ import annotations

from enum import Enum
from typing import Callable, Optional, Iterator, Any


class ConstructableMixin(Enum):
    @classmethod
    def table(cls):
        return {
            item.value: item for item in cls
        }

    @classmethod
    def from_str(cls, s: str):
        return cls.table()[s]

    @classmethod
    def is_valid(cls, s: str):
        return s in cls.table()


class LenPolicy(ConstructableMixin):
    """field length policy"""
    fixed = "fixed"
    auto = "auto"  # length is sum of children fields
    greedy = "greedy"
    dependency = "dependency"


class SizePolicy(ConstructableMixin):
    """field size policy, used in variable field"""
    fixed = "fixed"  # imply a non-variable field
    greedy = "greedy"
    dependency = "dependency"


class Dependency:
    def __init__(self, spec: tuple):
        assert len(spec) >= 1
        self.handler = spec[0]
        self.args = spec[1:]
        assert isinstance(self.handler, Callable)


class Tree:
    def __init__(self, parent: Optional[Tree], children: Optional[Iterator[Tree]]):
        self.parent = parent
        self.children = tuple(children) if children else tuple()

    @property
    def is_root(self):
        return self.parent is None

    def root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.root()

    @property
    def is_leaf(self):
        return len(self.children) == 0

    def find(
            self,
            condition: Callable[[Any], bool],
            visited: Optional[set] = None
    ) -> Optional[Tree]:
        """find first match of which condition() is True"""
        if not visited:
            visited = set()

        visited.add(self)
        if condition(self):
            return self

        nxt = list(self.children)
        if self.parent:
            nxt.append(self.parent)

        for t in nxt:
            if t not in visited:
                result = t.find(condition, visited)
                if result:
                    return result
        return None

    def add_children(self, *children: Tree) -> Tree:
        # some dirty works, doesn't really create a new tree
        tmp = list(self.children)
        for child in children:
            tmp.append(child)
        self.children = tuple(tmp)
        return self
