from pprint import pprint
from specification import decode
from specification import load


with open("test_specification.spec", "r") as fp:
    s = fp.read()

decoded = decode(s)
pprint(decoded, sort_dicts=False)

load(decoded)
