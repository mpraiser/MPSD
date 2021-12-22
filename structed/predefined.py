"""
predefined naming rules
"""

from typing import Any


STRUCTURAL_VARIABLE_PREFIX = "@"
INTERNAL_PREFIX = "_"
CALLABLE_PREFIX = "#"
PREFIXES = [
    STRUCTURAL_VARIABLE_PREFIX,
    INTERNAL_PREFIX,
    CALLABLE_PREFIX
]
PROPERTIES = "properties"
I_PROPERTIES = INTERNAL_PREFIX + PROPERTIES
LENGTH = "length"
SIZE = "size"
HANDLER = "handler"


def is_structural_variable_field(name: str) -> bool:
    return name.startswith(STRUCTURAL_VARIABLE_PREFIX)


def is_internal(label: str) -> bool:
    return label.startswith(INTERNAL_PREFIX)


def is_callable(label: str) -> bool:
    return label.startswith(CALLABLE_PREFIX)


def unwrap(name: str) -> str:
    """unwrap from the prefixes"""
    return name[1:]


def check_and_get(spec: dict, name: str, key: str) -> Any:
    if key not in spec:
        raise Exception(f"{key} not found in specification '{name}'")
    return spec[key]
