from structed.handler import bytes2int_b, bytes2hex


def handler_type(x: bytes) -> dict:
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


def handler_schedule_type(x: bytes) -> dict:
    raw = bytes2int_b(x)
    schedule_type = {
        0b000: "USCH Schedule",
        0b001: "DRX Schedule",
        0b010: "Registration Success Respond",
        0b011: "Uplink Receive Respond"
    }
    b7_b5 = (raw & 0b11100000) >> 5
    device_count = raw & 0b00011111
    return {
        "message_type": schedule_type[b7_b5],
        "device_count": device_count
    }


def handler_schedule_type_size(typ: dict) -> int:
    type2size = {
        "USCH Schedule": 4,
    }
    return type2size[typ["message_type"]]


def handler_schedule_type_len(typ: dict) -> int:
    return typ["device_count"]


def handler_schedule_type_content(typ: dict, raw: bytes):
    def handler_usch_schedule(r: bytes) -> tuple[str, tuple[int, int]]:
        slave_addr = bytes2hex(r[0:2])
        slot_start = r[2]
        slot_end = r[3]
        return slave_addr, (slot_start, slot_end)

    t = typ["message_type"]
    if t == "USCH Schedule":
        return handler_usch_schedule(raw)
