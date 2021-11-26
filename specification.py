import json
import handler
from collections.abc import Callable

from section import SizePolicy, Unit


VARIABLE_SECTION_PREFIX = "@"
INTERNAL_PREFIX = "_"
CALLABLE_PREFIX = "#"
PREFIXES = [
    VARIABLE_SECTION_PREFIX,
    INTERNAL_PREFIX,
    CALLABLE_PREFIX
]
PROPERTIES = INTERNAL_PREFIX + "properties"


def is_internal(label: str) -> bool:
    return label.startswith(INTERNAL_PREFIX)


def is_callable(label: str) -> bool:
    return label.startswith(CALLABLE_PREFIX)


def handler_handler(s: str) -> Callable:
    """convert str to a Callable in module handler"""
    name = unwrap(s)
    return getattr(handler, name)


def unwrap(label: str):
    """remove prefix and suffix"""
    return label[1:]


def is_valid_section(section: str):
    return not section.startswith(INTERNAL_PREFIX)


def is_variable_section(section: str):
    return section.startswith(VARIABLE_SECTION_PREFIX)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, DependencySpec):
        #     pass
        if isinstance(obj, Unit):
            return obj.value
        elif isinstance(obj, Callable):
            return CALLABLE_PREFIX + obj.__name__
        # default return
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):
    @staticmethod
    def hook(self):
        pass

    def __init__(self):
        super().__init__(object_hook=self.hook)


def encode(dct: dict) -> str:
    return Encoder().encode(dct)


def create_properties(dct: dict, label: str):
    # create _properties
    if PROPERTIES in dct:
        raise Exception(f"{PROPERTIES} cannot be a key of specification.")
    prop = {}
    to_remove = []
    for key in dct:
        if is_internal(key):
            prop[unwrap(key)] = dct[key]
            to_remove.append(key)
    for key in to_remove:
        dct.pop(key)
    check_properties(prop, is_variable_section(label))
    dct[PROPERTIES] = prop


def check_properties(prop: dict, is_variable: bool):
    # check properties
    if "unit" not in prop:
        prop["unit"] = Unit.byte
    else:
        prop["unit"] = Unit.from_str(prop["unit"])

    if "size" not in prop:
        prop["size"] = SizePolicy.auto
    else:
        if isinstance(prop["size"], list):
            if not is_callable(prop["size"][0]):
                raise Exception(f"the first argument should be handler.")
            else:
                prop["size"][0] = handler_handler(prop["size"][0])
            prop["size"] = tuple(prop["size"])

        elif isinstance(prop["size"], str):
            if Unit.is_valid(prop["size"]):
                prop["size"] = Unit[prop["size"]]
            else:
                prop["size"] = int(prop["size"])

    if "handler" not in prop:
        prop["handler"] = None
    else:
        if is_callable(prop["handler"]):
            prop["handler"] = handler_handler(prop["handler"])

    if "list_len" not in prop:
        if is_variable:
            prop["list_len"] = 1
        else:
            prop["list_len"] = None
    else:
        pass


def decode(s: str) -> dict:
    blank = json.JSONDecoder().decode(s)

    def postorder(dct: dict, label: str) -> dict:
        for key, raw in dct.items():
            if key != PROPERTIES and isinstance(raw, dict):
                postorder(raw, key)

        if PROPERTIES not in dct:
            dct[PROPERTIES] = {}
        check_properties(dct[PROPERTIES], is_variable_section(label))
        return dct

    return postorder(blank, "")
