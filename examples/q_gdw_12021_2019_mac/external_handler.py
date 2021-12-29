from typing import Any

from structed.handler import bytes2int_b, bytes2hex
from structed.field import LenPolicy


USCH_SCD = "USCH Schedule"
DRX_SCD = "DRX Schedule"
REG_ACK = "Registration Success Respond"
UL_ACK = "Uplink Receive Respond"


def h_mac_type(x: bytes) -> dict:
    raw = bytes2int_b(x)
    b7_b4 = (raw & 0b11110000) >> 4
    channel_type = {
        0b0000: "BCH",
        0b0001: "DCCH",
    }
    indicators = {
        "network": ((raw >> 3) & 0b1) != 0,
        "ack": ((raw >> 2) & 0b1) != 0,
        "mic": ((raw >> 1) & 0b1) != 0,
        "encrypt": (raw & 0b1) != 0,
    }
    return {
        "channel_type": channel_type[b7_b4],
        "indicators": indicators
    }


def h_schedule_type(x: bytes) -> dict:
    raw = bytes2int_b(x)
    schedule_type = {
        0b000: USCH_SCD,
        0b001: DRX_SCD,
        0b010: REG_ACK,
        0b011: UL_ACK
    }
    b7_b5 = (raw & 0b11100000) >> 5
    device_count = raw & 0b00011111
    return {
        "message_type": schedule_type[b7_b5],
        "device_count": device_count
    }


def h_schedule_len(typ: dict) -> int:
    type2size = {
        USCH_SCD: 4,
        DRX_SCD: 6,
        REG_ACK: 8
    }
    return type2size[typ["message_type"]]


def h_schedule_size(typ: dict) -> int:
    return typ["device_count"]


def h_schedule_content(typ: dict, raw: bytes):
    def h_usch(r: bytes) -> tuple[str, tuple[int, int]]:
        slave_addr = bytes2hex(r[0:2])
        slot_start = r[2]
        slot_end = r[3]
        return slave_addr, (slot_start, slot_end)

    def h_drx(r: bytes) -> tuple[str, int]:
        slave_addr = bytes2hex(r[0:2])
        sleep_time = bytes2int_b(r[2:6])
        return slave_addr, sleep_time

    def h_reg(r: bytes) -> tuple[str, str]:
        slave_gid = bytes2hex(r[0:4])
        slave_cid = bytes2hex(r[4:6])
        return slave_gid, slave_cid

    dispatcher = {
        USCH_SCD: h_usch,
        DRX_SCD: h_drx,
        REG_ACK: h_reg
    }
    t = typ["message_type"]
    return dispatcher[t](raw)


def h_usch_format(r: bytes) -> dict:
    r = int(r)
    return {
        "command_len": (r & 0b11111000) >> 3,
        "fragment_flag": (r >> 2) & 0b1 != 0,
        "resource_request_flag": (r >> 1) & 0b1 != 0
    }


def h_command_size(fmt: dict) -> int:
    return 1 if fmt["command_len"] > 0 else 0


def h_command_len(fmt: dict) -> int:
    return fmt["command_len"]


def h_command_type(r: bytes) -> str:
    r = int(r)
    if r == 0x00:
        return "ACK Respond"
    elif r == 0x01:
        return "Communication Parameter Report"
    elif 0x02 <= r <= 0x7f:
        return "Reserved"
    else:
        return "User Defined"


def h_command_content_len(ct: str) -> Any:
    table = {
        "ACK Respond": 1,
        "Communication Parameter Report": LenPolicy.greedy
    }
    return table[ct]


def h_command_content(ct: str) -> Any:
    pass


def h_resource_request_size(fmt: dict) -> int:
    return 1 if fmt["resource_request_flag"] else 0
