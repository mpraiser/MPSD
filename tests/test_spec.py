from section import byte, SizePolicy, ListLenPolicy, DependencySpec
from spec import spec_load
from parse import parse


def handler_type(x: bytes) -> str:
    __dict = {
        b"\x00": "BCH",
        b"\x01": "DCCH",
        b"\x02": "MCH",
        b"\x03": "DSCH",
        b"\x04": "URCH",
        b"\x05": "USCH"
    }
    return __dict[x]


def handler_payload_len(x: bytes) -> int:
    return int.from_bytes(x, byteorder="big")


def handler_schedule_type_size(typ: bytes) -> int:
    __dict = {
        b"\x00": 2,
        b"\x01": 4
    }
    return __dict[typ]


my_spec = {
    "header": {
        "type": {
            "_properties": {
                "unit": byte,
                "size": 1,
                "handler": handler_type
            }
        },
        "payload_len": {
            "_properties": {
                "unit": byte,
                "size": 1,
                "handler": handler_payload_len
            }
        }
    },
    "payload": {
        "_properties": {
            "size": DependencySpec(lambda x: x, "payload_len")
        },

        "main_address": {
            "_properties": {
                "unit": byte,
                "size": 2,
                "handler": lambda x: x
            }
        },
        "@schedules": {
            "_properties": {
                "unit": byte,
                "size": SizePolicy.auto,
                "list_len": ListLenPolicy.greedy,
            },
            "schedule_type": {
                "_properties": {
                    "unit": byte,
                    "size": 1,
                    "handler": lambda x: x
                }
            },
            "schedule_content": {
                "_properties": {
                    "unit": byte,
                    "size": DependencySpec(handler_schedule_type_size, "schedule_type"),
                    "handler": lambda x: x
                }
            }
        }
    },
    "footer": {
        "mic": {
            "_properties": {
                "unit": byte,
                "size": 2,
                "handler": lambda x: x
            }
        }
    }
}


class TestSpec:
    pass


spec = spec_load(my_spec, "my_frame")
# spec.show()

# print("-----------")
#
# for leaf in spec.leaves():
#     print(leaf.property_dict())

raw = b"\x01\x0a\xaa\xaa\x00\x03\x04\x01\x05\x06\x07\x08\xff\xff"
used = parse(spec, raw)
spec.show()
print(f"len(raw) = {len(raw)}, used = {used}")
