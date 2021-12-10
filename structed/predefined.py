from __future__ import annotations

from typing import Any

STRUCTURAL_VARIABLE_PREFIX = "@"
INTERNAL_PREFIX = "_"
CALLABLE_PREFIX = "#"
PREFIXES = [
    STRUCTURAL_VARIABLE_PREFIX,
    INTERNAL_PREFIX,
    CALLABLE_PREFIX
]
PROPERTIES = INTERNAL_PREFIX + "properties"
LENGTH = "length"
SIZE = "size"
HANDLER = "handler"


def is_structural_variable_field(name: str) -> bool:
    return name.startswith(STRUCTURAL_VARIABLE_PREFIX)


def check_and_get(spec: dict, name: str, key: str) -> Any:
    if key not in spec:
        raise Exception(f"{key} not found in specification '{name}'")
    return spec[key]