from typing import Any


def dict_get(properties: dict, name) -> Any:
    """
    Args:
        properties: dict of properties
        name: name of property
    """
    if name in properties:
        return properties[name]
    for key, item in properties.items():
        if type(item) == dict:
            result = dict_get(item, name)
            if result:
                return result
    return None


def dict_struct_copy(src: dict, dst=None):
    """
    copy dict structure, leaf node will be a empty dict
    """
    if dst is None:
        dst = dict()
    for key in src:
        dst[key] = dict()
        if type(src[key]) == dict:
            dict_struct_copy(src[key], dst[key])
    return dst
