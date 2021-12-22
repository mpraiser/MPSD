from pprint import pprint
from structed import decode, parse, load
from structed.handler import hex2bytes


with open("udp.json", "r") as fp:
    ipd = decode(fp.read())
    print(ipd)

with open("raw_bytes.txt", "r") as fp:
    raw_bytes = [hex2bytes(x.strip()) for x in fp]
    spec = load(ipd)
    for i, raw in enumerate(raw_bytes):
        # message = load(spec)
        # message.parse(raw)
        message = parse(spec, raw)
        print(f"Message {i}: {raw}")
        pprint(dict(message), sort_dicts=False)
