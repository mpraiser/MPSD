"""
main datastructure: field and specification
"""

from __future__ import annotations  # to allow forward references in type hint
from typing import Optional, Callable, Any
from collections.abc import Sequence, Iterator
from functools import partial

from structed import predefined
from structed.common import LenPolicy, SizePolicy, Dependency, Tree
from structed.predefined import check_and_get, unwrap


class Field(Tree):
    def __init__(
            self,
            name: str,
            raw: Optional[Sequence],
            value: Any,
            parent: Optional[Field],
            children: Optional[Iterator[Field]],
            *,
            is_virtual: bool = False,
            virtual_length: Optional[int] = None
    ):
        """
        virtual is used in 2 situations:
        1. LenPolicy.auto, after parsing actualize() should be called.
        2. Structural variable.
        """
        super().__init__(parent, children)
        self.name = name
        self.raw = raw
        self.value = value
        self.is_virtual = is_virtual
        self.virtual_length = virtual_length

        if not is_virtual:
            if raw is None:
                raise Exception(f"Only raw of virtual field can be None.")
            if virtual_length is not None:
                raise Exception(f"Only virtual field can have attribute virtual_length.")
        else:
            if virtual_length is None:
                self.virtual_length = 0

    @property
    def length(self):
        if self.is_virtual:
            return self.virtual_length
        else:
            return len(self.raw)

    def __iter__(self):
        for child in self.children:
            child: Field
            if child.is_leaf:
                yield child.name, child.value
            else:
                d = {k: v for k, v in iter(child)}
                yield child.name, d

    def get(self, name: str) -> Any:
        """get the value of a field"""
        field = self.find(
            lambda x: getattr(x, "name") == name and not getattr(x, "is_virtual")
        )
        if not field:
            raise Exception(f"Cannot get field '{name}'.")
        if not field.is_leaf:
            raise Exception(f"Cannot get value from non-leaf field '{field.name}'.")
        return field.value

    def handle_dependency(self, dependency: Dependency) -> Callable:
        return partial(
            dependency.handler,
            *(self.get(x) for x in dependency.args)
        )

    def actualize(self, raw: Sequence, value: Any) -> Field:
        """to set values of a virtual field"""
        assert self.is_virtual
        self.raw = raw
        self.value = value
        self.is_virtual = False
        return self

    def set_virtual_length(self, length: int) -> Field:
        assert self.is_virtual
        self.virtual_length = length
        return self


class Specification(Tree):
    def __init__(
            self,
            name: str,
            length: int | LenPolicy | Dependency,
            size: Optional[SizePolicy | Dependency],
            handler: Optional[Callable | Dependency],
            parent: Optional[Specification],
            children: Optional[Iterator[Specification]]
    ):
        super().__init__(parent, children)
        self.name = name
        self.length = length
        self.size = size
        self.handler = handler

    @property
    def is_structural_variable(self) -> bool:
        return self.size is not None

    @property
    def is_length_variable(self) -> bool:
        return not isinstance(self.size, int)

    def structural_template(self, count: int) -> Specification:
        """rename and erase the size policy"""
        name = unwrap(self.name) + f"[{count}]"
        return Specification(
            name, self.length, None, self.handler, self.parent, self.children
        )

    def parse_value(self, raw: Sequence, pf: Field) -> Any:
        """
        parse value of field
        :param raw:
        :param pf: partially parsed field
        :return: parsed value
        """
        if self.is_leaf:
            if isinstance(self.handler, Callable):
                return self.handler(raw)
            elif isinstance(self.handler, Dependency):
                assert pf is not None
                return pf.handle_dependency(self.handler)(raw)
        else:
            return None

    def parse(self, raw: Sequence, parent: Optional[Field] = None) -> Field:
        # dealing with structural variability
        if self.is_structural_variable:
            return self.__parse_structural_variable(raw, parent)
        else:
            return self.__parse(raw, parent)

    def __parse(self, raw: Sequence, parent: Optional[Field]) -> Field:
        # dealing with length variability
        # dispatch according to type of self.length
        if isinstance(self.length, int):
            return self.__parse_len_policy_fixed(raw, parent)
        elif isinstance(self.length, Dependency):
            return self.__parse_len_policy_dependency(raw, parent)
        elif isinstance(self.length, LenPolicy):
            match self.length:
                case LenPolicy.auto:
                    return self.__parse_len_policy_auto(raw, parent)
                case LenPolicy.greedy:
                    return self.__parse_len_policy_greedy(raw, parent)
                case _:
                    raise Exception(f"Unsupported length policy of field '{self.name}' : {self.length}")
        else:
            raise Exception(f"Unsupported length type of field '{self.name}' : {type(self.length)}")

    def __parse_len_policy_fixed(self, raw: Sequence, parent: Optional[Field]) -> Field:
        raw = raw[:self.length]
        field = Field(
            self.name, raw, self.parse_value(raw, parent), parent, None
        )

        used = 0
        for cs in self.children:
            cs: Specification
            cf = cs.parse(field.raw[used:], field)
            used += cf.length
            field = field.add_children(cf)
        if not self.is_leaf and used < field.length:
            print(f"Warning: child fields does not used all bytes of field '{field.name}'.")
        return field

    def __parse_len_policy_dependency(self, raw: Sequence, parent: Optional[Field]) -> Field:
        length = parent.handle_dependency(self.length)()
        raw = raw[:length]
        field = Field(
            self.name, raw, self.parse_value(raw, parent), parent, None
        )

        used = 0
        for cs in self.children:
            cs: Specification
            cf = cs.parse(field.raw[used:], field)
            used += cf.length
            field = field.add_children(cf)
        if not self.is_leaf and used < field.length:
            print(f"Warning: child fields does not used all bytes of field '{field.name}'.")
        return field

    def __parse_len_policy_auto(self, raw: Sequence, parent: Optional[Field]) -> Field:
        field = Field(
            self.name, b"", None, parent, None,
            is_virtual=True
        )

        used = 0
        for cs in self.children:
            cs: Specification
            cf = cs.parse(raw[used:], field)
            used += cf.length
            field = field.add_children(cf)
        raw = raw[:used]
        field = field.actualize(raw, self.parse_value(raw, parent))
        return field

    def __parse_len_policy_greedy(self, raw: Sequence, parent: Optional[Field]) -> Field:
        pass

    def __parse_structural_variable(self, raw: Sequence, parent: Optional[Field]) -> Field:
        # create a virtual parent
        virtual = Field(
            self.name, None, None, parent, None,
            is_virtual=True
        )
        # dispatch according to type of self.size
        if isinstance(self.size, Dependency):
            return self.__parse_size_policy_dependency(raw, virtual)
        elif isinstance(self.size, SizePolicy):
            match self.size:
                case SizePolicy.greedy:
                    return self.__parse_size_policy_greedy(raw, virtual)
                case _:
                    raise Exception(f"Unsupported size policy of field '{self.name}' : {self.size}")
        else:
            raise Exception(f"Unsupported size type of field '{self.name}' : {type(self.size)}")

    def __parse_size_policy_dependency(self, raw: Sequence, virtual: Optional[Field]) -> Field:
        used = 0
        size = virtual.handle_dependency(self.size)()
        for _ in range(size):
            cs = self\
                .structural_template(len(virtual.children))\
                .parse(raw[used:], virtual)
            used += cs.length
            virtual = virtual.add_children(cs)
        return virtual.set_virtual_length(used)

    def __parse_size_policy_greedy(self, raw: Sequence, virtual: Optional[Field]) -> Field:
        used = 0
        while used < len(raw):
            cs = self\
                .structural_template(len(virtual.children))\
                .parse(raw[used:], virtual)
            used += cs.length
            virtual = virtual.add_children(cs)
        return virtual.set_virtual_length(used)


def load(
        spec: dict,
        name: str = "root",
        parent: Optional[Specification] = None
) -> Specification:
    """unpack the properties in spec"""
    prop = check_and_get(spec, name, predefined.I_PROPERTIES)
    length = check_and_get(prop, name, predefined.LENGTH)
    size = check_and_get(prop, name, predefined.SIZE)
    handler = check_and_get(prop, name, predefined.HANDLER)

    if not isinstance(length, int):
        # is a length variable field
        if isinstance(length, str):
            if LenPolicy.is_valid(length):
                length = LenPolicy.from_str(length)
            else:
                raise Exception(f"invalid length policy of field '{name}': {length}.")
        elif isinstance(length, tuple):
            length = Dependency(length)
        else:
            raise Exception(f"Invalid length type of field '{name}': {type(length)}.")

    if size is not None:
        # is a structural variable field
        if isinstance(size, str):
            if SizePolicy.is_valid(size):
                size = SizePolicy.from_str(size)
            else:
                raise Exception(f"invalid size policy of field '{name}': {size}.")
        elif isinstance(size, tuple):
            size = Dependency(size)
        else:
            raise Exception(f"invalid size type of field '{name}': {size}")

    if handler is not None:
        if isinstance(handler, tuple):
            handler = Dependency(handler)

    # recursively build the scaffold
    fs = Specification(
        name, length, size, handler, parent, None
    )
    children = []
    for child_name, child_spec in spec.items():
        if child_name != predefined.I_PROPERTIES:
            children.append(load(child_spec, child_name, fs))
    return fs.add_children(*children)


def parse(
        scaffold: Specification,
        raw: Sequence,
        parent: Optional[Field] = None
) -> Field:
    return scaffold.parse(raw, parent)
