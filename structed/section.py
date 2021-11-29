from enum import Enum
from typing import Optional, Union
from collections.abc import Callable, Iterable
from collections import namedtuple, deque
from functools import cache


class Unit(Enum):
    byte = "byte"
    bit = "bit"

    @classmethod
    def table(cls):
        return {
            item.value: item for item in cls
        }

    @staticmethod
    def from_str(s: str):
        return Unit.table()[s]

    @staticmethod
    def is_valid(s: str):
        return s in Unit.table()


class SizePolicy(Enum):
    """section size policy"""
    static = "static"  # fixed size
    auto = "auto"  # size is sum of children
    greedy = "greedy"  # size is all remaining raw bytes, except fixed size of right child
    dependency = "dependency"


class ListLenPolicy(Enum):
    static = "static"  # fixed size
    greedy = "greedy"  # read as much bytes as possible
    dependency = "dependency"


bit = Unit.bit
byte = Unit.byte

DependencySpec = namedtuple("DependencySpec", ["handler", "dependency"])  # [Callable, str/Section]


class Section:
    """Data structure of specification and to parse frame"""

    def __init__(
            self,
            label: str,
            raw: Optional[bytes],
            unit: Unit,
            size: Union[int, SizePolicy, DependencySpec],
            handler: Optional[Callable],
            *,
            children: Optional[Iterable] = None,
            parent: Optional = None,
            list_len: Optional[Union[int, SizePolicy, DependencySpec]] = None,
            is_variable_section: bool = False,
            sub_sections_template: Optional[Iterable] = None
    ):
        """
        :param label:
        :param raw:
        :param children:
        :param parent:
        :param handler: None means no need to parse, thus value is None too.
        :param unit:
        :param size:
        :param list_len:
        """
        # frame properties
        self.label = label
        self.raw = raw
        # only leaf section can have value,
        # None means not leaf section, or not parsed yet.
        self.value = None

        # topology
        self.children = children if children else []  # list of Section
        self.parent = parent if parent else None

        # template of sub-sections, only used in variable section
        self.sub_sections_template = sub_sections_template if sub_sections_template else []

        # properties for parsing
        self.handler = handler  # value = handler(raw)
        self.unit = unit
        self.size = size
        self.is_variable_section = is_variable_section
        if self.is_variable_section:
            if list_len is None:
                raise Exception("Variable section must have a list_len (int or ListLenPolicy)!")
            self.list_len = list_len

    def add_child(self, child):
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent is None

    def leaves(self):
        def __leaves(node: Section):
            """dfs to search all leaves under self from left to right"""
            if node.is_leaf():
                yield node
            for child in node.children:
                for x in __leaves(child):
                    yield x

        return __leaves(self)

    def property_dict(self, full: bool = False):
        if not full:
            return {
                "label": self.label,
                "raw": self.raw,
                "unit": self.unit,
                "size": self.size,
                "value": self.value
            }

    def __iter__(self):
        for child in self.children:
            if child.is_leaf():
                yield child.label, child.value
            else:
                d = {k: v for k, v in iter(child)}
                yield child.label, d

    def show(self):
        """BFS to print self"""
        q = deque()
        q.append((self, 0))  # (node, depth)
        last_depth = -1
        while q:
            node, depth = q.popleft()
            if depth > last_depth:
                print("\n")
                print(f"Layer {depth}")
            print(node.property_dict())
            for child in node.children:
                q.append((child, depth + 1))
            last_depth = depth

    def preorder(self):
        """iterate child sections by preorder"""
        yield self
        for child in self.children:
            for section in child.preorder():
                yield section

    def postorder(self):
        """iterate child sections by postorder"""
        for child in self.children:
            for section in child.postorder():
                yield section
        yield self

    @cache
    def find(self, label: str) -> Optional:
        """find section with given label in children, None for not found"""
        if self.label == label:
            return self
        for child in self.children:
            result = child.find(label)
            if result:
                return result
        return None

    def find_in_ancestor_left_sub_tree(self, label: str) -> Optional:
        """return the nearest"""
        for sibling in self.siblings("left"):
            if sibling.label == label:
                return sibling
            result = sibling.find(label)
            if result:
                return result
        if self.parent:
            result = self.parent.find_in_ancestor_left_sub_tree(label)
            if result:
                return result
        return None

    def siblings(self, relationship: str = "all"):
        """
        get all/left/right siblings
        :param relationship: "all", "left", "right"
        :return:
        """
        modes = ("all", "left", "right")
        assert relationship in modes

        if not self.parent:
            return

        self_found = False
        for sibling in self.parent.children:
            if sibling is self:
                self_found = True
            else:
                if relationship == "left":
                    if not self_found:
                        yield sibling
                elif relationship == "right":
                    if self_found:
                        yield sibling
                else:
                    yield sibling

    def handle_size_dependency(self) -> int:
        """
        :return: size value according to dependency
        """
        assert isinstance(self.size, tuple)
        handler, label = self.size
        # TODO: support multiple dependencies
        dependency = self.find_in_ancestor_left_sub_tree(label)
        if not dependency:
            raise Exception(f"Dependency '{label}' is not found.")
        if not dependency.value:
            raise Exception(f"Dependency '{label}' is not parsed.")
        size = handler(dependency.value)
        # self.size = size
        return size

    def add_sub_section_template(self, sub_section_template):
        assert self.is_variable_section
        self.sub_sections_template.append(sub_section_template)

    def create_sub_section(self):
        """create a child from template of sub-section, but not linked to parent"""
        assert self.is_variable_section
        sub_section = Section(
            self.label[1:], None, self.unit, SizePolicy.auto, None,
        )
        for template in self.sub_sections_template:
            child = Section(
                template.label, None, template.unit, template.size, template.handler,
                parent=sub_section
            )
            sub_section.add_child(child)
        return sub_section

    def add_sub_section(self):
        """create a child from template of sub-section"""
        if not isinstance(self.list_len, int):
            self.list_len = 0
        label = self.label[1:] + f"[{self.list_len}]"  # ignore initial @, add [n]
        sub_section = Section(
            label, None, self.unit, SizePolicy.auto, None,
            parent=self
        )
        for template in self.sub_sections_template:
            child = Section(
                template.label, None, template.unit, template.size, template.handler,
                parent=sub_section
            )
            sub_section.add_child(child)
        self.list_len += 1
        return sub_section

    def parse(self, raw: bytes) -> int:
        """
        :param raw:
        :return: number of bytes used
        """
        if self.is_variable_section:
            return self.__parse_variable(raw)
        else:
            return self.__parse_non_variable(raw)

    def __set(self, raw: bytes) -> int:
        """set raw bytes of self"""
        self.raw = raw
        self.size = len(raw)
        if self.is_leaf():
            self.value = self.handler(self.raw)
        return self.size

    def __parse_non_variable(self, raw: bytes) -> int:
        # dispatch according to type of self.size
        if isinstance(self.size, int):
            return self.__parse_size_policy_fixed(raw)
        elif isinstance(self.size, tuple):
            return self.__parse_size_policy_dependency(raw)
        elif isinstance(self.size, SizePolicy):
            policy = self.size
            if policy == SizePolicy.auto:
                return self.__parse_size_policy_auto(raw)
            elif policy == SizePolicy.greedy:
                return self.__parse_size_policy_greedy(raw)
            else:
                raise Exception(f"Section '{self.label}' unsupported size policy: {policy}")
        else:
            raise Exception(f"Section '{self.label}' unsupported size type: {type(self.size)}")

    def __parse_size_policy_fixed(self, raw: bytes) -> int:
        # do pre-order
        used = self.__set(raw[:self.size])
        child_used = 0
        for child in self.children:
            child_used += child.parse(self.raw[child_used:])
        if not self.is_leaf() and child_used < self.size:
            print(f"Warning: raw of {self.label} not all used by child sections.")
        return used

    def __parse_size_policy_auto(self, raw: bytes) -> int:
        # do post-order
        used = 0
        for child in self.children:
            used += child.parse(raw[used:])
        self.__set(raw[:used])
        return used

    def __parse_size_policy_greedy(self, raw: bytes) -> int:
        used = self.__set(raw)
        # TODO: greedy condition check
        return used

    def __parse_size_policy_dependency(self, raw: bytes) -> int:
        size = self.handle_size_dependency()
        used = self.__set(raw[:size])
        child_used = 0
        for child in self.children:
            child_used += child.parse(self.raw[child_used:])
        if not self.is_leaf() and child_used < self.size:
            print(f"Warning: raw of {self.label} not all used by child sections.")
        return used

    def __parse_variable(self, raw: bytes) -> int:
        assert self.is_variable_section
        used = 0
        list_len = 0
        if isinstance(self.list_len, int):
            max_list_len = self.list_len
        elif isinstance(self.list_len, ListLenPolicy):
            policy = self.list_len
            if policy == ListLenPolicy.greedy:
                max_list_len = None
            else:
                raise Exception(f"Section '{self.label}' unsupported list len policy: {policy}")
        else:
            raise Exception(f"Section '{self.label}' unsupported list len type: {type(self.size)}")

        while used < len(raw) and ((not max_list_len) or max_list_len and list_len <= max_list_len):
            sub_section = self.create_sub_section()
            size = sub_section.parse(raw[used:])
            used += size
            self.add_child(sub_section)
            list_len += 1
        self.list_len = list_len
        return used


def load(root_spec: dict, root_label: str = "") -> Section:
    """Parse a specification dict to a Tree"""
    from structed.specification import PROPERTIES, is_variable_section

    def __spec_parse(spec: dict, label: str, parent: Optional[Section]) -> Section:

        prop = spec[PROPERTIES]
        node = Section(
            label, None, prop["unit"], prop["size"], prop["handler"],
            list_len=prop["list_len"], parent=parent,
            is_variable_section=is_variable_section(label)
        )

        for child_label in spec:
            if child_label == PROPERTIES:
                continue
            child = __spec_parse(spec[child_label], child_label, node)
            if node.is_variable_section:
                node.add_sub_section_template(child)
            else:
                node.add_child(child)
        return node

    root = __spec_parse(root_spec, root_label, None)
    return root


def parse(spec: dict, raw: bytes) -> Section:
    root = load(spec)
    root.parse(raw)
    return root
