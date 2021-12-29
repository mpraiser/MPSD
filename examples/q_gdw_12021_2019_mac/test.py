from pprint import pprint
from structed import decode, parse, load, add_external_handlers_from
from structed.handler import hex2bytes

import external_handler as ext


add_external_handlers_from(ext)


keys = ["dcch"]

for key in keys:
    with open(f"{key}.json", "r") as fp:
        ipd = decode(fp.read())
        pprint(ipd, sort_dicts=False)

    with open(f"raw_{key}.txt", "r") as fp:
        raw_bytes = [hex2bytes(x.strip()) for x in fp]
        spec = load(ipd)
        for i, raw in enumerate(raw_bytes):
            # message = load(spec)
            # message.parse(raw)
            message = parse(spec, raw)
            print(f"Message {i}: {raw}")
            pprint(dict(message), sort_dicts=False)
