def bytes2int_b(x: bytes) -> int:
    """byte order is big-endian"""
    return int.from_bytes(x, byteorder="big")


def bytes2hex(x: bytes) -> str:
    """convert the bytes to hex string"""
    return x.hex()


def identity(x: bytes) -> bytes:
    return x


def bytes2str(x: bytes) -> str:
    """interpret the bytes as ascii"""
    pass


def hex2bytes(h: str) -> bytes:
    return bytes(
        int(h[i:i + 2], base=16) for i in range(0, len(h), 2)
    )
