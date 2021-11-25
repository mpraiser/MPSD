from section import byte, DependencySpec
from functools import partial


def hex2int(x: bytes):
    return int.from_bytes(x, byteorder="big")


def bytes2hex(x: bytes):
    return x.hex()


spec = {
    "src_port": {
        "_properties": {
            "unit": byte,
            "size": 2,
            "handler": hex2int
        }
    },
    "dst_port": {
        "_properties": {
            "unit": byte,
            "size": 2,
            "handler": hex2int
        }
    },
    "length": {
            "_properties": {
                "unit": byte,
                "size": 2,
                "handler": hex2int
            }
        },
    "checksum": {
            "_properties": {
                "unit": byte,
                "size": 2,
                "handler": hex2int
            }
        },
    "data": {
        "_properties": {
                "unit": byte,
                "size": DependencySpec(lambda x: x, "length"),
                "handler": lambda x: x.hex()
            }
    }
}
