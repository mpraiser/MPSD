from structed.field import load, parse


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
    "_properties": {
        "length": "auto",
        "size": None,
        "handler": None,
    },
    "header": {
        "_properties": {
            "length": "auto",
            "size": None,
            "handler": None,
        },
        "type": {
            "_properties": {
                "length": 1,
                "size": None,
                "handler": handler_type,
            }
        },
        "payload_len": {
            "_properties": {
                "length": 1,
                "size": None,
                "handler": handler_payload_len
            }
        }
    },
    "payload": {
        "_properties": {
            "length": (lambda x: x, "payload_len"),
            "size": None,
            "handler": handler_payload_len,

        },

        "main_address": {
            "_properties": {
                "length": 2,
                "size": None,
                "handler": lambda x: x,
            }
        },
        "@schedules": {
            "_properties": {
                "length": "auto",
                "size": "greedy",
                "handler": None
            },
            "schedule_type": {
                "_properties": {
                    "length": 1,
                    "size": None,
                    "handler": lambda x: x,
                }
            },
            "schedule_content": {
                "_properties": {
                    "length": (handler_schedule_type_size, "schedule_type"),
                    "size": None,
                    "handler": lambda x: x
                }
            }
        }
    },
    "footer": {
        "_properties": {
            "length": "auto",
            "size": None,
            "handler": None
        },
        "mic": {
            "_properties": {
                "length": 2,
                "size": None,
                "handler": lambda x: x
            }
        }
    }
}


raw = b"\x01\x0a\xaa\xaa\x00\x03\x04\x01\x05\x06\x07\x08\xff\xff"
scaffold = load(spec)
field = parse(scaffold, raw)
print(dict(field))
