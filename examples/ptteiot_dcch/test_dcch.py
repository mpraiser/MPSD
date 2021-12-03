from pprint import pprint
from structed import decode, parse
from structed.specification import add_external_handler
from structed.handler import hex2bytes
from external_handler import *


add_external_handler(handler_type)
add_external_handler(handler_schedule_type)
add_external_handler(handler_schedule_type_content)
add_external_handler(handler_schedule_type_size)
add_external_handler(handler_schedule_type_len)


with open("dcch.json", "r") as fp:
    spec = decode(fp.read())
    pprint(spec, sort_dicts=False)

with open("raw_bytes.txt", "r") as fp:
    raw_bytes = [hex2bytes(x.strip()) for x in fp]
    for i, raw in enumerate(raw_bytes):
        # message = load(spec)
        # message.parse(raw)
        message = parse(spec, raw)
        print(f"Message {i}: {raw}")
        pprint(dict(message), sort_dicts=False)
