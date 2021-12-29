"""
JSON decoder and encoder for convert JSON into intermediate dict
"""

import json
from typing import Callable, Any

from structed import predefined, handler
from structed.common import LenPolicy


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Callable):
            return predefined.CALLABLE_PREFIX + obj.__name__
        # default return
        return json.JSONEncoder.default(self, obj)


class Decoder(json.JSONDecoder):
    @staticmethod
    def hook(obj: list[tuple[str, Any]]) -> dict:
        prop = dict()
        ret = dict()
        for name, value in obj:
            if predefined.is_internal(name):
                if predefined.unwrap(name) != predefined.PROPERTIES:
                    n, v = Decoder.decode_property(name, value)
                    prop[n] = v
            else:
                ret[name] = value

        prop = Decoder.check_default_value(prop)
        ret[predefined.I_PROPERTIES] = prop
        return ret

    @staticmethod
    def decode_property(name: str, value: Any) -> tuple[str, Any]:
        name = predefined.unwrap(name)
        match name:
            case predefined.LENGTH:
                if isinstance(value, list):
                    value = Decoder.check_dependency(value)
            case predefined.SIZE:
                if isinstance(value, list):
                    value = Decoder.check_dependency(value)
            case predefined.HANDLER:
                if isinstance(value, str):
                    value = Decoder.decode_callable(value)
                elif isinstance(value, list):
                    value = Decoder.check_dependency(value)
            case _:
                raise Exception(f"Invalid internal property name: '{name}'")
        return name, value

    @staticmethod
    def decode_callable(func_name: str) -> Callable:
        name = predefined.unwrap(func_name)
        if name == "":
            return getattr(handler, "identity")
        return getattr(handler, name)

    @staticmethod
    def check_dependency(dependency: list) -> tuple[Callable, str, ...]:
        if not predefined.is_callable(dependency[0]):
            raise Exception(f"When specify a dependency, "
                            f"the first argument should have prefix '{predefined.CALLABLE_PREFIX}'")
        dependency[0] = Decoder.decode_callable(dependency[0])
        return tuple(dependency)

    @staticmethod
    def check_default_value(prop: dict) -> dict:
        """if needed is not in prop, use default value"""
        if predefined.LENGTH not in prop:
            prop[predefined.LENGTH] = LenPolicy.auto.value
        if predefined.SIZE not in prop:
            prop[predefined.SIZE] = None
        if predefined.HANDLER not in prop:
            prop[predefined.HANDLER] = None
        return prop

    def __init__(self):
        super().__init__(object_pairs_hook=self.hook)


def add_external_handler(func: Callable):
    setattr(handler, func.__name__, func)


def add_external_handlers_from(mod):
    for func in mod.__dict__.values():
        if callable(func):
            add_external_handler(func)


def decode(raw: str) -> dict:
    return Decoder().decode(raw)
