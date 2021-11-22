from section import byte, SizePolicy, ListLenPolicy, DependencySpec
from specification import load
from section import Section


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


spec = {
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
raw = b"\x01\x0a\xaa\xaa\x00\x03\x04\x01\x05\x06\x07\x08\xff\xff"
root: Section = load(spec)
used = root.parse(raw)
root.show()
print(f"len(raw) = {len(raw)}, used = {used}")
