from spec import spec
from specification import load


def hex2bytes(gid: str) -> bytes:
    return bytes(
        int(gid[i:i + 2], base=16) for i in range(0, len(gid), 2)
    )


raw = "30391f40004ed20f2058866fffced06be212befd51b94c35d4d516568fc6b2de53d9a4bf665d747aa7f63da1a92982f27996b0f84ca9c4a87af7d3208864b35c17e207d52788afc270a359fc498e"
raw = hex2bytes(raw)
root = load(spec)
root.parse(raw)
print(dict(root))

