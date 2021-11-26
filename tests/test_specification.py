from pprint import pprint
from specification import decode
from section import load

with open("test_specification_spec.json", "r") as fp:
    s = fp.read()

decoded = decode(s)
pprint(decoded, sort_dicts=False)

load(decoded)
